"""TM3-009 baseline evidence examples; independent output layer, no decoder changes.
Run: .venv/bin/python src/report_tm3_009_baseline.py
Only writes the two new Markdown attachments and baseline_evidence/ provenance.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
import cantools
from asc_dbc_signal_trace import parse_asc_line

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'output/TM3-009'
OUT = BASE / 'report_v1'
DETAIL = OUT / 'baseline_evidence'
ASC = ROOT / 'input/can_20260831090233_TM3-010_中等负载加速采集.asc'
SOURCES = {'O': ROOT/'input/tesla_model3_ONYX.dbc', 'M': ROOT/'dbc/Model3CAN.dbc'}
NAMES = ['采集时间线与关键Signal.md', 'DBC关键Signal覆盖与可读性.md']
# role, frame, signal, source, purpose, maximum past-sample age (seconds)
REG = []
def add(role, fid, names, purpose, age=.15, source='O'):
    for name in names.split(): REG.append((role, fid, name, source, purpose, age))
add('驾驶输入',0x118,'DI_accelPedalPos','识别真实踩下、调节及归零时刻',.03)
add('条件/状态',0x118,'DI_gear DI_systemState','区分P/STANDBY与D/ENABLE',.03)
add('条件/状态',0x118,'DI_driveBlocked DI_tractionControlMode','保留状态观测；不单凭字段名判定实际阻止驱动或介入',.03)
add('仲裁后请求',0x108,'DI_torqueCommand','最终电驱请求；不等同电门原始请求')
add('执行反馈',0x108,'DI_torqueActual','与同帧请求配对，保留瞬态差值')
add('运动反馈',0x108,'DI_axleSpeed','轴速，与扭矩同帧；非电机转子转速')
add('运动反馈',0x257,'DI_vehicleSpeed','首次运动、达速、调速与停车',.05)
add('能源响应',0x266,'DI_elecPower','电驱电功率，与Pack功率相互印证',.03)
add('能源响应',0x132,'BMS_packVoltage BMS_packCurrent','保存电压/电流对应关系，同帧派生Pack功率',.03)
add('制动输入',0x39D,'IBST_sInputRodDriver','输入杆位移，不等于制动力或液压',.08,'M')
add('制动状态',0x39D,'IBST_driverBrakeApply IBST_internalState IBST_iBoosterStatus','区分施加、释放过程及助力状态',.08,'M')
add('制动状态',0x3C2,'VCLEFT_brakeSwitchPressed VCLEFT_brakePressed','制动开关边沿；不量化制动力')
add('制动状态/不可用',0x118,'DI_brakePedalState','全程INVALID，排除其作为制动施加判据',.03)
add('条件/能力',0x268,'DI_sysDrivePowerMax DI_sysRegenPowerMax','能力候选，保留数值；未验证约束阈值')
add('条件/能力',0x2D2,'BMS_maxDischargeCurrent BMS_maxChargeCurrent','电池能力候选；不是本次实测输出电流')
add('条件/SOC',0x292,'BMS_socUI','本次SOC背景，不外推整个SOC范围')
add('条件/解码失败',0x252,'BMS_maxDischargePower BMS_maxRegenPower','主DBC重叠导致解码失败，不填作零')
add('制动请求/缺失',0x145,'ESP_brakeTorqueTarget','有定义但本采集域无帧，不能验证制动力请求')
add('制动执行/缺失',0x185,'ESP_brakeTorqueFL ESP_brakeTorqueFR ESP_brakeTorqueRL ESP_brakeTorqueRR ESP_brakeTorqueQF','有定义但无帧，不把输入杆换算成轮端制动力')


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def num(v): return isinstance(v,(float,int)) and math.isfinite(v)
def norm(v): return float(v) if num(v) else str(v)
def fmt(v):
    if v is None: return '—'
    if num(v): return f'{v:.6f}'.rstrip('0').rstrip('.')
    return str(v).replace('|','/').replace('\n',' ')
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(fmt(v) for v in row)+' |' for row in rows])+'\n'
def csvout(name,rows):
    with (DETAIL/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def signature(s):
    return dict(start=s.start,length=s.length,byte_order=s.byte_order,signed=s.is_signed,
                scale=s.scale,offset=s.offset,unit=s.unit,mux=s.multiplexer_ids,
                choices={str(k):str(v) for k,v in (s.choices or {}).items()})
def needed(s):
    if s.byte_order=='little_endian': return (s.start+s.length+7)//8
    bit=s.start; positions=[]
    for _ in range(s.length):
        positions.append(bit);bit=bit+15 if bit%8==0 else bit-1
    return max(positions)//8+1


def main():
    assert sha(ASC)=='c9f378fa919ead3fb7464395d1b33b92c97a1ffca156371191bfc4545bf3b4e6'
    assert sha(SOURCES['O'])=='3554e37a3a8371bc9c1b76445061d30f2c5bbaa35a055fe1f01f7ee75030e86c'
    inventory=json.loads((BASE/'dbc_brake_audit/inventory.json').read_text())
    assert sha(SOURCES['M'])==next(x['sha256'] for x in inventory if x['file']=='Model3CAN.dbc')
    protected=list((ROOT/'input').rglob('*.asc'))+list((ROOT/'dbc').glob('*'))+list(SOURCES.values())
    protected += [p for p in BASE.rglob('*') if p.is_file() and DETAIL not in p.parents and p.name not in NAMES]
    protected += [ROOT/'src'/n for n in ['analyze_tm3_009.py','analyze_tm3_009_braking.py','audit_brake_dbcs.py','report_tm3_009.py']]
    before={str(p.relative_to(ROOT)):sha(p) for p in protected if p.is_file()}
    DETAIL.mkdir(parents=True,exist_ok=True)
    db={k:cantools.database.load_file(p,strict=False) for k,p in SOURCES.items()}
    series=defaultdict(list); times={}; frames=Counter(); dlcs=defaultdict(Counter); errors=defaultdict(Counter)
    raw_by_id=defaultdict(list); last=0; count=0
    wanted={r[1] for r in REG}
    for line in ASC.open(encoding='utf-8'):
        f=parse_asc_line(line)
        if not f: continue
        count+=1;last=f['time'];fid=f['can_id'];t=f['time']
        if fid not in wanted:continue
        frames[fid]+=1;dlcs[fid][f['dlc']]+=1;raw_by_id[fid].append((t,f['data']))
        source='M' if fid==0x39D else 'O'
        try: vals=db[source].get_message_by_frame_id(fid).decode(f['data'],decode_choices=True,allow_truncated=True)
        except Exception as e:
            errors[fid][str(e)]+=1;continue
        for _,i,name,_,_,_ in REG:
            if i==fid and name in vals:series[name].append((t,norm(vals[name])))
        if fid==0x132 and num(vals.get('BMS_packVoltage')) and num(vals.get('BMS_packCurrent')):
            series['PackPower_derived'].append((t,vals['BMS_packVoltage']*vals['BMS_packCurrent']/1000))
        if fid==0x39D:
            assert vals['IBST_sInputRodDriver']==((int.from_bytes(f['data'],'little')>>21)&4095)/64-5
    assert count==483669 and last==169.9696
    for n,s in series.items():times[n]=[t for t,v in s]
    # Native samples must match retained engineering outputs, not only summaries.
    compared=0
    with (BASE/'signal_samples.csv').open(encoding='utf-8-sig') as f:
        old=defaultdict(list)
        for r in csv.DictReader(f):
            if r['signal'] in series:
                try:v=float(r['value'])
                except ValueError:v=r['value']
                old[r['signal']].append((float(r['time_s']),v))
    for n,s in old.items():assert s==series[n],n;compared+=len(s)
    index={r[2]:r for r in REG}
    def at(n,t):
        age=.03 if n=='PackPower_derived' else index[n][-1]
        i=bisect_right(times.get(n,[]),t)-1
        if i<0 or t-times[n][i]>age+1e-9:return None,None
        return series[n][i][1],times[n][i]
    def first(n,a,b,predicate):return next(t for t,v in series[n] if a<=t<b and predicate(v))
    events=[]
    def event(t,label,criterion,planned='—'):events.append(dict(time_s=t,event=label,criterion=criterion,planned_s=planned))
    event(.15,'初始P挡参考状态','固定首段参考点（非动作边沿）；待关键报文到齐',0)
    old_summary=json.loads((BASE/'summary.json').read_text())
    for runno,run in enumerate(old_summary['runs'],1):
        a,b=run['drive_window'];prefix=f'第{runno}轮'
        event(a,prefix+'挂D','DI_gear 首个D样本',20 if runno==1 else 95)
        release=first('VCLEFT_brakeSwitchPressed',a,b,lambda v:v==0)
        event(release,prefix+'制动开关释放','VCLEFT_brakeSwitchPressed 首个0；不等同输入杆完全回零')
        event(first('DI_torqueCommand',a,b,lambda v:num(v) and v>0),prefix+'零电门正请求建立','D挡内 DI_torqueCommand 首个>0')
        event(first('DI_vehicleSpeed',a,b,lambda v:num(v) and v>.5),prefix+'观察到低速运动','DI_vehicleSpeed 首个>0.5 km/h；识别阈值非标定阈值')
        event(run['pedal_onset_s'],prefix+'开始踩电门','DI_accelPedalPos 首个>0',30 if runno==1 else 105)
        # Independent peak events avoid synthesizing simultaneous maxima.
        for n,label in [('DI_torqueCommand','请求峰值'),('DI_torqueActual','实际扭矩峰值'),('DI_accelPedalPos','电门峰值'),('DI_elecPower','电驱功率峰值'),('BMS_packCurrent','Pack放电电流峰值'),('DI_vehicleSpeed','车速峰值')]:
            s=[(t,v) for t,v in series[n] if run['pedal_onset_s']<=t<b and num(v)]
            t,v=max(s,key=lambda p:p[1]);assert t==run['stats'][n]['peak_s']
            event(t,prefix+label,f'{n} 在本轮踩电门起点至离开D挡前的最大值（首次出现）')
        event(run['first_30kmh_s'],prefix+'首次达到30 km/h','DI_vehicleSpeed 首个≥30',45 if runno==1 else 120)
        req=[(t,v) for t,v in series['DI_torqueCommand'] if a<=t<b]
        for (prev,pv),(t,v) in zip(req,req[1:]):
            if num(pv) and num(v) and pv>=0 and v<0:
                event(t,prefix+'请求转负','DI_torqueCommand 从≥0变为<0；单独识别调速/减速')
                end=next((tt for tt,vv in req if tt>t and num(vv) and vv>=0),b)
                net=next((tt for tt,vv in series['PackPower_derived'] if t<=tt<end and vv<0),None)
                if net is not None:event(net,prefix+'负请求期间首次观察到Pack净回收','本次负请求区间内，Pack同帧V×I首次<0；不据时间差推算系统延迟')
            if num(pv) and num(v) and pv<0 and v>=0:event(t,prefix+'请求退出负值','DI_torqueCommand 从<0变为≥0')
        pedal_off=first('DI_accelPedalPos',run['pedal_onset_s']+.1,b,lambda v:v==0)
        event(pedal_off,prefix+'电门完全归零','踩下后 DI_accelPedalPos 首次回到0',55 if runno==1 else 130)
        event(first('DI_vehicleSpeed',pedal_off,b,lambda v:abs(v)<=.5),prefix+'减速至近零车速','电门归零后 |DI_vehicleSpeed| 首个≤0.5km/h；不等同精确机械停稳时刻')
        event(b,prefix+'回P','DI_gear 离开D进入P的首个样本',75 if runno==1 else 150)
    # All five actual brake intervals, including post-park holding, are retained.
    bs=series['IBST_driverBrakeApply'];episodes=[];start=None
    for t,v in bs:
        if v=='DRIVER_APPLYING_BRAKES' and start is None:start=t
        elif v!='DRIVER_APPLYING_BRAKES' and start is not None:
            rod=[(tt,vv) for tt,vv in series['IBST_sInputRodDriver'] if start<=tt<t]
            peak=max(rod,key=lambda x:x[1]);episodes.append((start,t,*peak))
            event(start,'制动施加状态出现','IBST_driverBrakeApply 首个 DRIVER_APPLYING_BRAKES')
            event(t,'制动施加状态解除','IBST_driverBrakeApply 首个 BRAKES_NOT_APPLIED')
            start=None
    for t,label in [(98.2595,'补踩制动：请求仍处高值'),(98.6767,'补踩制动：输入杆行程峰值'),(99.4592,'补踩制动：正请求降至62 Nm'),(99.6594,'输入杆回落中请求已恢复'),(99.959,'施加状态解除后的扭矩样本')]:
        event(t,label,'已核实的独立制动工况关键原生样本')
    event(last,'采集结束','最后一个ASC数据帧',170)
    events.sort(key=lambda e:e['time_s'])
    for i,e in enumerate(events,1):e['event_id']=f'E{i:02}'
    snapnames=['DI_gear','DI_systemState','DI_accelPedalPos','DI_torqueCommand','DI_torqueActual','DI_axleSpeed','DI_vehicleSpeed','DI_elecPower','BMS_packVoltage','BMS_packCurrent','PackPower_derived','IBST_sInputRodDriver','IBST_driverBrakeApply','IBST_internalState','VCLEFT_brakeSwitchPressed','BMS_socUI']
    snapshots=[]; long=[]
    for e in events:
        r=dict(e)
        for n in snapnames:
            v,t=at(n,e['time_s']);r[n]=v
            reg=index.get(n);fid=reg[1] if reg else 0x132
            long.append(dict(event_id=e['event_id'],event_time_s=e['time_s'],event=e['event'],signal=n,can_id=f'0x{fid:03X}',value=v,sample_time_s=t,age_ms=None if t is None else round((e['time_s']-t)*1000,6),unit=(db[reg[3]].get_message_by_frame_id(fid).get_signal_by_name(n).unit or 'enum/raw') if reg else 'kW',source=str(SOURCES[reg[3]].relative_to(ROOT)) if reg else 'derived: BMS_packVoltage * BMS_packCurrent / 1000, same frame',status='available' if t is not None else 'missing_or_stale'))
        snapshots.append(r)
    csvout('event_signal_samples.csv',long)
    csvout('events.csv',events)
    # All model3-named DBC variants: aliases by exact name, then same start bit
    # and length OR known role alias. Candidate matching never promotes semantics.
    paths=sorted(p for p in (ROOT/'dbc').iterdir() if 'model3' in p.name.lower() and '.dbc' in p.name.lower())
    variants={str(p.relative_to(ROOT)):cantools.database.load_file(p,database_format="dbc",strict=False) for p in paths}
    alias={'DI_torqueCommand':'DIR_torqueCommand','DI_torqueActual':'DIR_torqueActual','DI_axleSpeed':'DIR_axleSpeed','BMS_packVoltage':'BattVoltage132','BMS_packCurrent':'SmoothBattCurrent132','DI_vehicleSpeed':'DI_vehicleSpeed','DI_elecPower':'DI_elecPower'}
    definitions=[]; coverage=[]
    for role,fid,n,source,purpose,age in REG:
        m=db[source].get_message_by_frame_id(fid);s=m.get_signal_by_name(n);ss=series[n]
        invalid=[(t,v) for t,v in ss if not num(v) and any(x in v for x in ['INVALID','SNA','NOT_INIT','FAULT'])]
        invalid_times={t for t,v in invalid};valid=[v for t,v in ss if t not in invalid_times];ns=[v for v in valid if num(v)]
        value_range=f'{fmt(min(ns))}～{fmt(max(ns))}' if ns else (' / '.join(sorted(set(map(str,valid)))) or '—')
        needed_dlc=max([needed(s)]+[needed(x) for x in m.signals if x.is_multiplexer and s.multiplexer_signal==x.name])
        flag=[]
        if needed_dlc>m.length:flag.append('DBC声明DLC小于Signal所需长度；仅ASC足长才可读')
        if any(d<m.length for d in dlcs[fid]):flag.append('ASC短于DBC；逐Signal检查完整性')
        if any(d<needed_dlc for d in dlcs[fid]):flag.append('存在不足以承载本Signal的帧')
        if invalid:flag.append(f'INVALID/SNA/未初始化/FAULT {len(invalid)}样本，不作有效物理值')
        if errors[fid]:flag.append('解码失败：'+str(dict(errors[fid])))
        if not frames[fid]:flag.append('本ASC无帧')
        if n=='DI_driveBlocked':flag.append('raw=2；M映射DRIVE_BLOCKED_PROX，但实车可驱动，不据此判定阻止驱动')
        if n=='IBST_sInputRodDriver':flag.append('O没有该定义；采用M的21|12、×0.015625−5 mm')
        if n=='DI_sysRegenPowerMax':flag.append('SNA枚举不同：O为155，M无枚举，旧版为255；物理缩放一致，能力阈值仍未验证')
        if n=='DI_elecPower':flag.append('同名异位：O位0，旧版位16；本次仅采用O，不可跨版本直接套用')
        diff=[]
        for path,other in variants.items():
            try:om=other.get_message_by_frame_id(fid)
            except KeyError:
                definitions.append(dict(signal=n,can_id=f'0x{fid:03X}',dbc=path,message='',dbc_dlc='',candidate='',relation='无Message',definition=''));continue
            candidates=[x for x in om.signals if x.name==n]
            relation='同名'
            if not candidates:
                candidates=[x for x in om.signals if x.name==alias.get(n)];relation='明确名称别名候选'
            if not candidates:
                candidates=[x for x in om.signals if x.start==s.start and x.length==s.length and x.is_multiplexer==s.is_multiplexer and x.multiplexer_ids==s.multiplexer_ids];relation='仅位段相同候选，非语义确认'
            if not candidates:
                definitions.append(dict(signal=n,can_id=f'0x{fid:03X}',dbc=path,message=om.name,dbc_dlc=om.length,candidate='',relation='无对应Signal',definition=''));continue
            for os in candidates:
                same=signature(os)==signature(s)
                if not same:diff.append(path)
                definitions.append(dict(signal=n,can_id=f'0x{fid:03X}',dbc=path,message=om.name,dbc_dlc=om.length,candidate=os.name,relation=relation+('；参数一致' if same else '；参数差异'),definition=json.dumps(signature(os),ensure_ascii=False,sort_keys=True)))
        if diff:flag.append('跨DBC参数/枚举差异，见版本对照')
        periods=[b[0]-a[0] for a,b in zip(ss,ss[1:])]
        coverage.append(dict(role=role,message=m.name,signal=n,can_id=f'0x{fid:03X}',unit=s.unit or 'enum/raw',source=source,dbc_dlc=m.length,signal_required_dlc=needed_dlc,asc_dlc='/'.join(map(str,sorted(dlcs[fid]))) or '无帧',frames=frames[fid],decoded=len(ss),invalid=len(invalid),changed='是' if len(set(v for t,v in ss))>1 else ('否' if ss else '未知'),valid_range=value_range,dbc_range=f'{s.minimum}～{s.maximum}',period_ms=round(median(periods)*1000,3) if periods else None,purpose=purpose,flags='；'.join(flag) or '所选Signal长度完整',definition=json.dumps(signature(s),ensure_ascii=False,sort_keys=True)))
    csvout('signal_coverage.csv',coverage);csvout('dbc_definition_comparison.csv',definitions)
    # Explicitly measure the effect of the 15-bit/16-bit Pack-current definition.
    packdiff=[]
    for t,data in raw_by_id[0x132]:
        ov=db['O'].get_message_by_frame_id(0x132).decode(data,allow_truncated=True)['BMS_packCurrent']
        mv=db['M'].get_message_by_frame_id(0x132).decode(data,allow_truncated=True)['SmoothBattCurrent132']
        if not math.isclose(ov,mv,abs_tol=1e-9):packdiff.append(dict(time_s=t,raw=data.hex(' '),ONYX_A=ov,Model3CAN_A=mv))
    if packdiff:csvout('pack_current_definition_disagreements.csv',packdiff)
    version_values=[]
    for n,fid,path,alias_name in [
        ('DI_elecPower',0x266,'dbc/Model3CAN.dbc','RearPower266'),
        ('DI_elecPower',0x266,'dbc/tesla_model3.dbc','DI_elecPower'),
        ('DI_sysRegenPowerMax',0x268,'dbc/Model3CAN.dbc','SystemRegenPowerMax268'),
        ('DI_sysRegenPowerMax',0x268,'dbc/tesla_model3.dbc','DI_sysRegenPowerMax')]:
        vals=[];failed=0
        for t,data in raw_by_id[fid]:
            try:v=variants[path].get_message_by_frame_id(fid).decode(data,allow_truncated=True)[alias_name]
            except Exception:failed+=1;continue
            if num(v):vals.append(v)
        version_values.append(dict(signal=n,other_dbc=path,other_signal=alias_name,numeric_samples=len(vals),failed_frames=failed,minimum=min(vals) if vals else None,maximum=max(vals) if vals else None))
    csvout('dbc_variant_observations.csv',version_values)
    timeline=['# TM3-009 采集时间线与关键Signal','',
      '用途：车型基线证据层。按实际数据重建状态、动作及关键节点值；不扩充最终报告，不作车辆故障判定。',
      '', '车辆：上海产2021款Model 3，2021年5月出厂，标准续航55 kWh，后驱。',
      f'原始文件：`{ASC.relative_to(ROOT)}`（原文件名编号为TM3-010，按中等负载加速脚本归属TM3-009，不改名）。共{count}帧；末帧{last:.4f}s。',
      '', '## 读取规则', '',
      '时间均为ASC相对秒。计划时间仅来自脚本，未取得独立触发CSV，计划与观察的差值不是精确驾驶反应延迟。事件时刻为首次观察或明确标出的参考采样点。',
      '每个事件采用该时刻及之前最近的有效样本，不插值、不取未来值；扭矩/轴速150ms、电门/状态/电功率/Pack量30ms、车速50ms、IBST 80ms、VC制动开关150ms、SOC150ms为最大允许样本年龄。具体采样时间及年龄保存在同名事件明细中。—表示无样本或超龄，不表示零。',
      '同一事件编号连接下面三张表。峰值各自建事件，其他列是该事件附近的实际状态，不把不同时间的峰值拼成一行。Pack功率由同帧电压×电流/1000派生；本报告沿用ONYX符号，正值为放电方向，负值为净回收方向，和电驱功率分别记录，不用二者差值直接计算效率。',
      '', '## 实际时间线', '',table(['事件','实际s','计划s','实际状态/动作','数据判据'],[(e['event_id'],e['time_s'],e['planned_s'],e['event'],e['criterion']) for e in events]),
      '## 控制与动力关键值', '',
      '列名：挡位=`DI_gear (0x118)`；系统=`DI_systemState (0x118)`；电门=`DI_accelPedalPos (0x118)`；请求/实际=`DI_torqueCommand / DI_torqueActual (0x108)`；轴速=`DI_axleSpeed (0x108)`；车速=`DI_vehicleSpeed (0x257)`。', '',
      table(['事件','时刻s','挡位/系统','电门%','请求Nm','实际Nm','轴速RPM','车速km/h'],[(r['event_id'],r['time_s'],str(r['DI_gear'])+'/'+str(r['DI_systemState']),r['DI_accelPedalPos'],r['DI_torqueCommand'],r['DI_torqueActual'],r['DI_axleSpeed'],r['DI_vehicleSpeed']) for r in snapshots]),
      '## 同事件能源与制动关键值', '',
      '电驱=`DI_elecPower (0x266)`；Pack V/I=`BMS_packVoltage / BMS_packCurrent (0x132)`；输入杆=`IBST_sInputRodDriver (0x39D)`；施加=`IBST_driverBrakeApply (0x39D)`（ON=DRIVER_APPLYING_BRAKES，OFF=BRAKES_NOT_APPLIED）；内部状态=`IBST_internalState (0x39D)`；开关=`VCLEFT_brakeSwitchPressed (0x3C2)`。', '',
      table(['事件','电驱kW','Pack V','Pack A','Pack kW（派生）','输入杆mm','施加','内部状态','开关'],[(r['event_id'],r['DI_elecPower'],r['BMS_packVoltage'],r['BMS_packCurrent'],r['PackPower_derived'],r['IBST_sInputRodDriver'],{'DRIVER_APPLYING_BRAKES':'ON','BRAKES_NOT_APPLIED':'OFF'}.get(r['IBST_driverBrakeApply'],r['IBST_driverBrakeApply']),r['IBST_internalState'],r['VCLEFT_brakeSwitchPressed']) for r in snapshots]),
      '## 工况区间及采集偏差', '',
      table(['状态/动作','实际区间或节点s','基线用途'],[
      ('第1轮踩电门至首次30km/h','27.4225～44.9230','加速主窗口，电门前已低速运动；沿用最终报告2.34Nm MAE'),
      ('第2轮踩电门至首次30km/h','102.0783～120.1169','加速主窗口，补踩制动后进入；沿用2.58Nm MAE'),
      ('脚本第1次保持30km/h','45～55','实测30.24～34.72km/h；51.762起请求转负，不作为严格稳态样本'),
      ('脚本第2次保持30km/h','120～130','实测29.44～32.56km/h；125.4562起请求转负'),
      ('第1轮调速与完全松电门','51.762转负、57.7611退出负值；71.9601再次转负、72.019归零','请求可在电门仍>0时转负；55s计划减速不能替代真实动作'),
      ('第2轮松电门','125.4562请求转负；140.4659电门归零','130s脚本减速并非完全松电门时刻'),
      ('独立低速制动交互','98.0368～99.9574（IBST施加区间）','与加速主窗口分开；正请求下降未归零，释放过程中已恢复')]),
      '制动状态区间采用左闭右开：起点为施加首次出现，终点为首次解除；峰值为该区间内输入杆的独立峰值，不等同制动力。', '',
      table(['施加起点s','解除s','杆行程峰值时刻s','杆行程峰值mm'],episodes),
      '98～100s关键对照：98.2595s请求/实际382/388 Nm；99.4592s为62/104 Nm；99.6594s恢复至110/90 Nm时仍为施加状态。99.9574s施加状态解除，99.9590s扭矩为332/330 Nm。初期请求仍上升、随后下降、杆回落时已恢复，不能表述为“一踩立即下降、完全松开后才恢复”。近零车速−0.16km/h不据此判为倒车。',
      '', '## 追溯与基线保存', '',
      '控制链记录驾驶输入、条件/仲裁后请求、执行及运动；能源侧独立保存V/I/P与电驱功率对应值。全部事件还保存SOC及各Signal原始采样时间，供后续车型投射和条件化基线入库。所见范围是本次观测范围，不是车型正常限值。',
      '[事件Signal值与采样时刻](baseline_evidence/event_signal_samples.csv) · [事件判据](baseline_evidence/events.csv) · [DBC覆盖附件](DBC关键Signal覆盖与可读性.md) · [既有工程审计](工程审计.md)',
      '复现命令：`.venv/bin/python src/report_tm3_009_baseline.py`。该命令只生成两个新附件及其追溯文件。']
    (OUT/NAMES[0]).write_text('\n'.join(timeline)+'\n',encoding='utf-8')
    report=['# TM3-009 DBC关键Signal覆盖与可读性','',
      '用途：车型基线证据层。以控制树角色选择字段，Signal语义为主、CAN ID为原始数据追溯键。成功解码、物理有效、语义适用于本车是三个不同判断。',
      '', '## 来源与表格约定', '',
      '`O`＝`input/tesla_model3_ONYX.dbc`（与`dbc/tesla_model3_ONYX.dbc.txt`相同）；`M`＝`dbc/Model3CAN.dbc`（与同名`.txt`相同）。主报告沿用O；IBST输入杆与内部状态采用M。',
      '下表DLC单位为字节；“需要”是承载该Signal及其复用选择器的最小长度。“解码”是实际出现的Signal样本数/所属Message帧数，复用字段不要求每帧出现。“变化”包含原始状态变化；“有效范围”剔除INVALID/SNA等状态，不把失败、无帧记作零。',
      '', '## 控制树角色覆盖', '']
    for group in ['驾驶输入','条件','仲裁后请求','执行反馈','运动反馈','能源响应','制动']:
        rows=[c for c in coverage if c['role'].startswith(group)]
        report += ['### '+group,'',table(['角色','Message','Signal（CAN ID）','单位','来源','DBC/需要/ASC DLC','解码 样本/帧','变化','有效观测范围/状态','本次用途'],[(c['role'],c['message'],c['signal']+' ('+c['can_id']+')',c['unit'],c['source'],f"{c['dbc_dlc']}/{c['signal_required_dlc']}/{c['asc_dlc']}",f"{c['decoded']}/{c['frames']}",c['changed'],c['valid_range'],c['purpose']) for c in rows])]
    report += ['Pack功率（派生，非DBC原生Signal）：`BMS_packVoltage (0x132) × BMS_packCurrent (0x132) / 1000`，单位kW；同帧计算，DBC来源O，电压/电流均完整时有效。观测范围'+fmt(min(v for t,v in series['PackPower_derived']))+'～'+fmt(max(v for t,v in series['PackPower_derived']))+' kW。用途为电池能源响应；正放电/负净回收。',
      '', '## 需要明确标记的可读性问题', '',
      table(['Signal（CAN ID）','标记与处理'],[(c['signal']+' ('+c['can_id']+')',c['flags']) for c in coverage if c['flags']!='所选Signal长度完整']),
      '本次所选主定义没有“DBC DLC小于本Signal所需长度而ASC足够”的实例，不能把其他采集中的例子套用进来；格式已单列需要长度，遇到此情况须标记并记录实际采用的解码长度。',
      '`BMS_packVoltage / BMS_packCurrent (0x132)`：O声明8字节，实车6字节，但分别只需2/4字节，因此这两个Signal完整；同Message尾部其他Signal不一定可读。`IBST_sInputRodDriver (0x39D)`：O仅声明3字节且没有此字段，M定义需5字节，实车5字节；采用M不是对O补长。',
      '`BMS_maxDischargePower / BMS_maxRegenPower (0x252)`：O包含BMS_hvacPowerBudget与BMS_inverterTQF重叠定义，本次1699帧全部解码失败；M没有该重叠字段。附件保留原失败，不切换DBC来覆盖原报告结果。',
      '', '## 跨DBC差异及其影响', '',
      table(['角色/字段','定义差异','本次处理'],[
      ('Pack电流：BMS_packCurrent / SmoothBattCurrent132 (0x132)','O：start16、15位有符号、×−0.1；M：start16、16位有符号、×−0.1',f'逐帧对照16997帧，数值不同{len(packdiff)}帧。继续使用O，不能把定义差异抹成等价'),
      ('DI_torqueCommand / DI_torqueActual / DI_axleSpeed (0x108)','M采用DIR_前缀，正常物理缩放一致；SNA枚举键为+4096、+32768，O为−4096、−32768','保留当前O；本次未遇到这些哨兵，不据此确认全量定义等价'),
      ('DI_elecPower (0x266)','O start0，旧版tesla_model3.dbc同名字段start16；M的RearPower266位段与O相同，但无SNA枚举','采用O；同名不同位置属于实质定义冲突，不能直接替换。各版本读数范围见下表'),
      ('DI_sysRegenPowerMax (0x268)','三版均start32、8位、×1、偏置−100；O的SNA枚举键155，M无枚举，旧版为255','本次三版均读出91～92 kW；保留能力候选，不把本次未触及的SNA差异忽略或直接确认为限制阈值'),
      ('DI_driveBlocked (0x118)','O没有枚举，M将2映射DRIVE_BLOCKED_PROX','当前值2与能驱动同时出现；只记raw=2，不判实际阻断'),
      ('IBST_sInputRodDriver / IBST_internalState (0x39D)','M及party包含5字节扩展；O/旧版3字节缺字段','来自M；杆位移逐帧通过原始位提取交叉核对'),
      ('BMS_maxDischargePower / BMS_maxRegenPower (0x252)','O报文存在重叠，M结构不同','保留主定义解码失败，未来按版本单独验证')]),
      '跨版本扫描覆盖`dbc/`内全部文件名含model3的DBC及其`.txt`副本。对同名、明确别名及同位段候选逐一保留Message、DLC、位定义、缩放、枚举与差异；同位段只是候选，不自动等同语义。其他泛Tesla字典的制动专项对比继续保留在既有工程审计。',
      '',table(['主Signal（CAN ID）','对照DBC','对照Signal','本次对照解码范围','数值样本/失败帧'],[(r['signal']+' ('+f"0x{index[r['signal']][1]:03X}"+')',r['other_dbc'],r['other_signal'],fmt(r['minimum'])+'～'+fmt(r['maximum']),str(r['numeric_samples'])+'/'+str(r['failed_frames'])) for r in version_values]),
      '这些对照值仅说明换用定义对读数的影响，未替换主DBC结果，也不将对照候选直接纳入已确认基线。',
      '', '## 工程追溯入口', '',
      '[完整Signal覆盖表（含采样周期、定义、标记）](baseline_evidence/signal_coverage.csv) · [全部Model3版本定义对照](baseline_evidence/dbc_definition_comparison.csv) · [源文件及保护校验](baseline_evidence/verification.json) · [既有制动DBC审计](../dbc_brake_audit/制动DBC规格对比.md) · [工程审计](工程审计.md)',
      '这层回答关键节点是否可见、读出了什么、为何采用或排除；完整原始帧、逐样本解码、DLC与错误记录留在工程审计，不扩充最终报告正文。']
    (OUT/NAMES[1]).write_text('\n'.join(report)+'\n',encoding='utf-8')
    for p,h in before.items():assert sha(ROOT/p)==h,'protected file changed: '+p
    verify=dict(frames=count,duration_s=last,event_count=len(events),event_signal_rows=len(long),coverage_signals=len(coverage),matched_prior_native_samples=compared,pack_current_cross_dbc_difference_frames=len(packdiff),pack_current_difference_examples=packdiff[:3],rod_raw_bit_verified=frames[0x39D],source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [ASC,*SOURCES.values(),*paths]},protected_files_sha256=before,all_protected_unchanged=True)
    (DETAIL/'verification.json').write_text(json.dumps(verify,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in verify.items() if k not in ['source_hashes','protected_files_sha256']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
