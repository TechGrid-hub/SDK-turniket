from hikvision_sdk import HikvisionSDK

sdk = HikvisionSDK("sdk")
user_id = sdk.login("192.168.8.8", 8000, "admin", "techgrid70")

# Yuz rasm yuklash yoki aniqlash bo'yicha boshqa funksiyalar...

sdk.logout(user_id)
sdk.cleanup()