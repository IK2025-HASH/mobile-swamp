[app]
title = MobileSwamp
package.name = mobileswamp
package.domain = com.poc
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2
requirements = python3,kivy==2.3.0
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 34
android.minapi = 24
android.ndk = 27c
android.ndk_api = 24
android.private_storage = True
android.accept_sdk_license = True
android.arch = arm64-v8a
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
