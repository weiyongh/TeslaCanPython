package com.teslacan.voicerunner;

import android.app.*;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.*;
import android.graphics.drawable.GradientDrawable;
import android.media.*;
import android.net.Uri;
import android.os.*;
import android.provider.OpenableColumns;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.view.*;
import android.widget.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.util.*;

public class MainActivity extends Activity implements TextToSpeech.OnInitListener {
    private static final int OPEN=10, SAVE=11, BLUE=Color.rgb(61,111,198), ORANGE=Color.rgb(246,126,37);
    private final Handler handler=new Handler();
    private final List<String> events=new ArrayList<>();
    private List<ScriptStep> steps=new ArrayList<>();
    private TextView fileName,timer,current,countdown,next;
    private Button runButton;
    private TextToSpeech tts;
    private ToneGenerator tone;
    private String scriptText="", scriptName="内置示例脚本.txt";
    private boolean running,preparing,preRollStarted,ttsReady;
    private long baseMs;
    private int fired=-1,announced=-1,lastBeep=-1;

    private final Runnable tick=new Runnable(){ public void run(){
        if(!running)return;
        long elapsedMs=SystemClock.elapsedRealtime()-baseMs;
        int elapsed=(int)(elapsedMs/1000L);
        timer.setText(clock(elapsed%3600));
        int i=upcoming(elapsed);
        if(i>=0){
            ScriptStep s=steps.get(i); int remain=s.second-elapsed;
            if(remain<=5&&i!=announced){announced=i;speak("准备，"+s.title);}
            if(remain>=1&&remain<=3){
                countdown.setText(String.valueOf(remain));
                if(lastBeep!=remain){lastBeep=remain;tone.startTone(ToneGenerator.TONE_PROP_BEEP,120);}
            }else if(remain<=0) fire(i,elapsedMs);
            else {countdown.setText("—");lastBeep=-1;}
        }else countdown.setText("—");
        handler.postDelayed(this,100);
    }};

    @Override public void onCreate(Bundle b){super.onCreate(b);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);
        tts=new TextToSpeech(this,this);tone=new ToneGenerator(AudioManager.STREAM_MUSIC,90);
        buildUi();loadSample();
    }

    private void buildUi(){
        LinearLayout root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(18),dp(12),dp(18),dp(14));root.setBackgroundColor(Color.WHITE);root.setFitsSystemWindows(true);
        LinearLayout top=new LinearLayout(this);top.setGravity(Gravity.CENTER);
        top.addView(button("导入脚本",v->openScript()),buttonLp());
        top.addView(button("查看脚本",v->showScript()),buttonLp());root.addView(top,matchWrap());
        fileName=text("",16,Color.DKGRAY);fileName.setGravity(Gravity.CENTER);fileName.setSingleLine();
        fileName.setEllipsize(android.text.TextUtils.TruncateAt.MIDDLE);root.addView(fileName,matchWrap());
        root.addView(new Space(this),space(0.65f));
        timer=text("00:00",48,Color.rgb(15,31,47));timer.setTypeface(Typeface.create("sans-serif-light",0));timer.setGravity(Gravity.CENTER);root.addView(timer,matchWrap());
        current=text("尚未开始",25,Color.rgb(25,25,25));current.setGravity(Gravity.CENTER);current.setPadding(4,dp(10),4,dp(10));root.addView(current,matchWrap());
        FrameLayout circle=new FrameLayout(this);GradientDrawable bg=new GradientDrawable();bg.setShape(GradientDrawable.OVAL);bg.setColor(ORANGE);circle.setBackground(bg);
        countdown=text("—",58,Color.WHITE);countdown.setGravity(Gravity.CENTER);circle.addView(countdown,new FrameLayout.LayoutParams(-1,-1));
        LinearLayout.LayoutParams cp=new LinearLayout.LayoutParams(dp(190),dp(190));cp.gravity=Gravity.CENTER;cp.setMargins(0,dp(10),0,dp(16));root.addView(circle,cp);
        root.addView(new Space(this),space(.35f));
        next=text("下一操作：—",20,Color.rgb(30,30,30));next.setGravity(Gravity.CENTER);next.setPadding(4,dp(8),4,dp(8));root.addView(next,matchWrap());
        root.addView(new Space(this),space(1f));
        runButton=button("开始采集",v->toggle());LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(dp(180),dp(58));rp.gravity=Gravity.CENTER;root.addView(runButton,rp);
        setContentView(root);
    }

    private void toggle(){
        if(running||preparing){stop(running);return;} if(steps.isEmpty()){toast("请先导入脚本");return;}
        events.clear();events.add("planned_s,actual_s,event");fired=announced=lastBeep=-1;
        timer.setText("00:00");current.setText("准备开始采集");countdown.setText("—");
        preparing=true;preRollStarted=false;runButton.setText("结束采集");showNext(0);
        if(ttsReady)speak("准备开始采集","pre_start");
        else handler.postDelayed(this::beginPreRoll,1800);
    }
    private void beginPreRoll(){if(!preparing||preRollStarted)return;preRollStarted=true;preRoll(3,"三");handler.postDelayed(()->preRoll(2,"二"),1000);handler.postDelayed(()->preRoll(1,"一"),2000);handler.postDelayed(this::beginTimedRun,3000);}
    private void preRoll(int value,String voice){if(!preparing)return;countdown.setText(String.valueOf(value));speak(voice);tone.startTone(ToneGenerator.TONE_PROP_BEEP,120);}
    private void beginTimedRun(){
        if(!preparing)return;preparing=false;running=true;baseMs=SystemClock.elapsedRealtime();timer.setText("00:00");countdown.setText("开始");speak("开始采集");
        if(!steps.isEmpty()&&steps.get(0).second==0)fire(0,0);else{current.setText("开始采集");showNext(0);}
        handler.post(tick);
    }
    private void stop(boolean export){running=false;preparing=false;preRollStarted=false;handler.removeCallbacksAndMessages(null);if(tts!=null)tts.stop();runButton.setText("开始采集");countdown.setText("—");
        if(export&&events.size()>1)new AlertDialog.Builder(this).setTitle("采集已结束").setMessage("是否导出本次实际事件时间？")
                .setNegativeButton("暂不导出",null).setPositiveButton("导出记录",(d,w)->saveEvents()).show();}
    private void fire(int i,long elapsedMs){if(i<=fired)return;fired=i;ScriptStep s=steps.get(i);current.setText(s.title);countdown.setText("执行");
        tone.startTone(ToneGenerator.TONE_PROP_ACK,260);events.add(s.second+","+String.format(Locale.US,"%.3f",elapsedMs/1000d)+",\""+s.title.replace("\"","\"\"")+"\"");showNext(i+1);
        if(i==steps.size()-1){speak("采集完成");stop(true);}}
    private int upcoming(int sec){for(int i=fired+1;i<steps.size();i++)if(steps.get(i).second>=sec)return i;return-1;}
    private void showNext(int i){next.setText(i>=0&&i<steps.size()?"下一操作： "+clock(steps.get(i).second)+"  "+steps.get(i).title:"下一操作： 已完成");}

    private void openScript(){startActivityForResult(new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("text/*").addCategory(Intent.CATEGORY_OPENABLE),OPEN);}
    private void showScript(){new AlertDialog.Builder(this).setTitle(scriptName).setMessage(scriptText.isEmpty()?"尚未载入脚本":scriptText).setPositiveButton("关闭",null).show();}
    private void saveEvents(){startActivityForResult(new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("text/csv").putExtra(Intent.EXTRA_TITLE,"CAN事件_"+new SimpleDateFormat("yyyyMMdd_HHmmss",Locale.CHINA).format(new Date())+".csv"),SAVE);}
    @Override protected void onActivityResult(int req,int result,Intent data){super.onActivityResult(req,result,data);if(result!=RESULT_OK||data==null||data.getData()==null)return;
        try{if(req==OPEN){Uri u=data.getData();scriptName=queryName(u);load(read(u));}else if(req==SAVE){write(data.getData(),String.join("\n",events));toast("记录已导出");}}catch(Exception e){toast("操作失败："+e.getMessage());}}
    private String queryName(Uri u){try(Cursor c=getContentResolver().query(u,null,null,null,null)){if(c!=null&&c.moveToFirst()){int i=c.getColumnIndex(OpenableColumns.DISPLAY_NAME);if(i>=0)return c.getString(i);}}return"采集脚本.txt";}
    private String read(Uri u)throws IOException{try(InputStream in=getContentResolver().openInputStream(u);ByteArrayOutputStream out=new ByteArrayOutputStream()){if(in==null)throw new IOException("无法读取文件");byte[]b=new byte[4096];int n;while((n=in.read(b))>0)out.write(b,0,n);return out.toString("UTF-8");}}
    private void write(Uri u,String s)throws IOException{try(OutputStream out=getContentResolver().openOutputStream(u)){if(out==null)throw new IOException("无法创建文件");out.write(s.getBytes(StandardCharsets.UTF_8));}}
    private void load(String raw){steps=ScriptParser.parse(raw);stop(false);scriptText=raw;fileName.setText(scriptName);timer.setText("00:00");current.setText(steps.get(0).title);showNext(steps.size()>1?1:0);toast("已载入 "+steps.size()+" 个操作节点");}
    private void loadSample(){try(InputStream in=getAssets().open("sample_script.txt");ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[]b=new byte[4096];int n;while((n=in.read(b))>0)out.write(b,0,n);load(out.toString("UTF-8"));}catch(Exception e){toast("示例脚本载入失败："+e.getMessage());}}

    private void speak(String s){speak(s,"step_"+SystemClock.uptimeMillis());}
    private void speak(String s,String id){if(tts!=null)tts.speak(s,TextToSpeech.QUEUE_FLUSH,null,id);}
    private String clock(int sec){int v=Math.floorMod(sec,3600);return String.format(Locale.CHINA,"%02d:%02d",v/60,v%60);}
    private Button button(String s,View.OnClickListener l){Button b=new Button(this);b.setText(s);b.setTextSize(18);b.setTextColor(Color.WHITE);b.setAllCaps(false);b.setBackgroundColor(BLUE);b.setOnClickListener(l);return b;}
    private TextView text(String s,int size,int color){TextView v=new TextView(this);v.setText(s);v.setTextSize(size);v.setTextColor(color);return v;}
    private LinearLayout.LayoutParams buttonLp(){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,dp(54),1);p.setMargins(dp(5),0,dp(5),0);return p;}
    private LinearLayout.LayoutParams matchWrap(){return new LinearLayout.LayoutParams(-1,-2);}
    private LinearLayout.LayoutParams space(float w){return new LinearLayout.LayoutParams(1,0,w);}
    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_LONG).show();}
    @Override public void onInit(int status){if(status==TextToSpeech.SUCCESS){ttsReady=true;tts.setLanguage(Locale.SIMPLIFIED_CHINESE);tts.setSpeechRate(.92f);tts.setOnUtteranceProgressListener(new UtteranceProgressListener(){
        @Override public void onStart(String id){}
        @Override public void onError(String id){if("pre_start".equals(id))runOnUiThread(()->beginPreRoll());}
        @Override public void onDone(String id){if("pre_start".equals(id))runOnUiThread(()->beginPreRoll());}
    });}}
    @Override protected void onDestroy(){handler.removeCallbacks(tick);if(tts!=null)tts.shutdown();if(tone!=null)tone.release();super.onDestroy();}
}
