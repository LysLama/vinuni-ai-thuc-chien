import os
import shutil
import subprocess
import zipfile
import sys

BASE_DIR = os.path.abspath("D:/proj")
BUILD_DIR = os.path.join(BASE_DIR, "android_build")
SDK_DIR = r"C:\Users\thanh\AppData\Local\Android\Sdk"
BUILD_TOOLS_DIR = os.path.join(SDK_DIR, r"build-tools\34.0.0")
AAPT2 = os.path.join(BUILD_TOOLS_DIR, "aapt2.exe")
D8 = os.path.join(BUILD_TOOLS_DIR, "d8.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS_DIR, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS_DIR, "apksigner.bat")
JAVAC = r"C:\Program Files\Eclipse Adoptium\jdk-25.0.4.7-hotspot\bin\javac.exe"
ANDROID_JAR = os.path.join(SDK_DIR, r"platforms\android-34\android.jar")
KEYSTORE = os.path.join(BUILD_DIR, "debug.keystore")

def run(cmd, cwd=BASE_DIR):
    if isinstance(cmd, list):
        print(f"--> Running: {' '.join(str(c) for c in cmd)}")
        res = subprocess.run(cmd, cwd=cwd, shell=False, capture_output=True, text=True)
    else:
        print(f"--> Running: {cmd}")
        res = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"STDOUT: {res.stdout}")
        print(f"STDERR: {res.stderr}")
        raise RuntimeError(f"Command failed with code {res.returncode}")
    if res.stdout:
        print(res.stdout.strip())
    return res.stdout

def setup_directories():
    os.makedirs(os.path.join(BUILD_DIR, "res", "drawable"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "res", "values"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "src", "edu", "vinuni", "aithucchien"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "build", "obj"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "build", "dex"), exist_ok=True)
    os.makedirs(os.path.join(BUILD_DIR, "assets", "web"), exist_ok=True)

    # Copy launcher icon
    icon_src = os.path.join(BASE_DIR, "web", "icons", "icon-192.png")
    icon_dst = os.path.join(BUILD_DIR, "res", "drawable", "ic_launcher.png")
    shutil.copy2(icon_src, icon_dst)

    # Copy web assets to assets/web
    web_dst = os.path.join(BUILD_DIR, "assets", "web")
    if os.path.exists(web_dst):
        shutil.rmtree(web_dst)
    shutil.copytree(os.path.join(BASE_DIR, "web"), web_dst)
    print("Assets synced to android_build/assets/web")

def create_manifest():
    manifest_path = os.path.join(BUILD_DIR, "AndroidManifest.xml")
    content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="edu.vinuni.aithucchien"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-sdk
        android:minSdkVersion="26"
        android:targetSdkVersion="34" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:label="VinUni AI Thực Chiến"
        android:icon="@drawable/ic_launcher"
        android:theme="@android:style/Theme.NoTitleBar"
        android:hardwareAccelerated="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(content)

def create_strings():
    values_path = os.path.join(BUILD_DIR, "res", "values", "strings.xml")
    content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">VinUni AI Thực Chiến</string>
</resources>
"""
    with open(values_path, "w", encoding="utf-8") as f:
        f.write(content)

def create_main_activity():
    src_path = os.path.join(BUILD_DIR, "src", "edu", "vinuni", "aithucchien", "MainActivity.java")
    content = """package edu.vinuni.aithucchien;

import android.app.Activity;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.Window;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);

        webView = new WebView(this);
        setContentView(webView);

        WebView.setWebContentsDebuggingEnabled(true);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        settings.setUseWideViewPort(false);
        settings.setLoadWithOverviewMode(false);
        settings.setSupportZoom(false);
        settings.setDisplayZoomControls(false);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(android.webkit.ConsoleMessage cm) {
                android.util.Log.d("VinUniApp", cm.message() + " [L" + cm.lineNumber() + "]");
                return true;
            }
        });
        webView.clearCache(true);

        webView.loadUrl("file:///android_asset/web/index.html");
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView != null && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
"""
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("=== Step 1: Setting up Directories & Source Code ===")
    setup_directories()
    create_manifest()
    create_strings()
    create_main_activity()

    print("=== Step 2: aapt2 compile ===")
    res_zip = os.path.join(BUILD_DIR, "build", "compiled_res.zip")
    res_dir = os.path.join(BUILD_DIR, "res")
    run([AAPT2, "compile", "--dir", res_dir, "-o", res_zip])

    print("=== Step 3: aapt2 link ===")
    temp_apk = os.path.join(BUILD_DIR, "build", "temp.apk")
    manifest = os.path.join(BUILD_DIR, "AndroidManifest.xml")
    assets_dir = os.path.join(BUILD_DIR, "assets")
    src_dir = os.path.join(BUILD_DIR, "src")
    run([
        AAPT2, "link",
        "-o", temp_apk,
        "-I", ANDROID_JAR,
        "--manifest", manifest,
        "-R", res_zip,
        "--java", src_dir,
        "-A", assets_dir,
        "--auto-add-overlay"
    ])

    print("=== Step 4: Compile Java Code (javac) ===")
    obj_dir = os.path.join(BUILD_DIR, "build", "obj")
    # Collect all java files (MainActivity.java + generated R.java)
    java_files = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".java"):
                java_files.append(os.path.join(root, f))
    
    javac_cmd = [JAVAC, "-d", obj_dir, "-classpath", ANDROID_JAR, "--release", "11"] + java_files
    run(javac_cmd)

    print("=== Step 5: Convert Class files to DEX (d8) ===")
    dex_dir = os.path.join(BUILD_DIR, "build", "dex")
    class_files = []
    for root, _, files in os.walk(obj_dir):
        for f in files:
            if f.endswith(".class"):
                class_files.append(os.path.join(root, f))
    
    d8_cmd = [D8, "--lib", ANDROID_JAR, "--output", dex_dir] + class_files
    # Note: d8.bat is a batch file, so shell=True is needed on Windows
    run(" ".join(f'"{c}"' for c in d8_cmd))

    print("=== Step 6: Add classes.dex into APK ===")
    classes_dex = os.path.join(dex_dir, "classes.dex")
    with zipfile.ZipFile(temp_apk, "a") as z:
        z.write(classes_dex, "classes.dex")
    print("classes.dex injected successfully into temp.apk")

    print("=== Step 7: zipalign ===")
    aligned_apk = os.path.join(BUILD_DIR, "build", "aligned.apk")
    if os.path.exists(aligned_apk):
        os.remove(aligned_apk)
    run([ZIPALIGN, "-f", "-p", "4", temp_apk, aligned_apk])

    print("=== Step 8: Sign APK (apksigner) ===")
    final_apk = os.path.join(BASE_DIR, "VinUniAIThucChien.apk")
    if os.path.exists(final_apk):
        os.remove(final_apk)
    
    apksigner_cmd = [
        APKSIGNER, "sign",
        "--ks", KEYSTORE,
        "--ks-pass", "pass:android",
        "--key-pass", "pass:android",
        "--out", final_apk,
        aligned_apk
    ]
    run(" ".join(f'"{c}"' for c in apksigner_cmd))

    print("=== Step 9: Verify APK ===")
    verify_cmd = [APKSIGNER, "verify", final_apk]
    run(" ".join(f'"{c}"' for c in verify_cmd))

    size_mb = os.path.getsize(final_apk) / (1024 * 1024)
    print(f"\n=======================================================")
    print(f"SUCCESS: Built {final_apk}")
    print(f"APK Size: {size_mb:.2f} MB")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
