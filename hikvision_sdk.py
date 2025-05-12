import os
import ctypes
from ctypes import *

# --- Yordamchi strukturalar ---
class NET_DVR_FACELIB_COND(Structure):
    _fields_ = [
        ("dwSize", c_uint),
        ("byFaceLibID", c_char * 36),
        ("byFaceData", c_void_p),
        ("dwFaceDataSize", c_uint)
    ]

class NET_DVR_FACERECOG_RESULT(Structure):
    _fields_ = [
        ("dwSize", c_uint),
        ("byFaceLibID", c_char * 36),
        ("byFaceData", c_void_p),
        ("dwFaceDataSize", c_uint),
        ("byRes", c_byte * 256)
    ]

# --- Asosiy wrapper klass ---
class HikvisionSDK:
    def __init__(self, sdk_path: str):
        self.sdk_path = os.path.abspath(sdk_path)
        os.add_dll_directory(self.sdk_path)
        self.sdk = ctypes.CDLL(os.path.join(self.sdk_path, 'HCNetSDK.dll'))

        if not self.sdk.NET_DVR_Init():
            raise Exception("HCNetSDK yuklanmadi (NET_DVR_Init xato).")
        print("[+] SDK muvaffaqiyatli yuklandi.")

    def cleanup(self):
        self.sdk.NET_DVR_Cleanup()
        print("[+] SDK tozalandi.")

    def login(self, ip, port, username, password):
        class NET_DVR_DEVICEINFO_V30(Structure):
            _fields_ = [
                ("sSerialNumber", c_byte * 48),
                ("byAlarmInPortNum", c_byte),
                ("byAlarmOutPortNum", c_byte),
                ("byDiskNum", c_byte),
                ("byDVRType", c_byte),
                ("byChanNum", c_byte),
                ("byStartChan", c_byte),
                ("byAudioChanNum", c_byte),
                ("byIPChanNum", c_byte),
                ("byZeroChanNum", c_byte),
                ("byMainProto", c_byte),
                ("bySubProto", c_byte),
                ("bySupport", c_byte),
                ("bySupport1", c_byte),
                ("bySupport2", c_byte),
                ("wDevType", c_ushort),
                ("bySupport3", c_byte),
                ("byMultiStreamProto", c_byte),
                ("byStartDChan", c_byte),
                ("byStartDTalkChan", c_byte),
                ("byHighDChanNum", c_byte),
                ("bySupport4", c_byte),
                ("byLanguageType", c_byte),
                ("byVoiceInChanNum", c_byte),
                ("byStartVoiceInChanNo", c_byte),
                ("bySupport5", c_byte),
                ("bySupport6", c_byte),
                ("byMirrorChanNum", c_byte),
                ("wStartMirrorChanNo", c_ushort),
                ("bySupport7", c_byte),
                ("byRes2", c_byte * 2)
            ]

        device_info = NET_DVR_DEVICEINFO_V30()
        login_id = self.sdk.NET_DVR_Login_V30(
            ip.encode('utf-8'), port, username.encode('utf-8'),
            password.encode('utf-8'), byref(device_info)
        )
        if login_id < 0:
            print("[-] Login muvaffaqiyatsiz:", self.sdk.NET_DVR_GetLastError())
        else:
            print("[+] Qurilmaga ulanish muvaffaqiyatli, UserID:", login_id)
        return login_id

    def logout(self, user_id):
        if self.sdk.NET_DVR_Logout(user_id):
            print("[+] Logout muvaffaqiyatli.", user_id)
        else:
            print("[-] Logoutda xatolik:", self.sdk.NET_DVR_GetLastError())

    def upload_face_picture(self, user_id, image_path, face_lib_id):
        if user_id < 0:
            print("[-] Yuz rasmini yuklash uchun foydalanuvchi ID noto‘g‘ri.")
            return False
        if not os.path.exists(image_path):
            print("[-] Rasm fayli topilmadi:", image_path)
            return False

        with open(image_path, 'rb') as file:
            img_data = file.read()

        face_data_buffer = ctypes.create_string_buffer(img_data)

        face_lib_cond = NET_DVR_FACELIB_COND()
        face_lib_cond.dwSize = sizeof(NET_DVR_FACELIB_COND)
        face_lib_cond.byFaceLibID = face_lib_id.encode('utf-8')
        face_lib_cond.byFaceData = ctypes.cast(face_data_buffer, c_void_p)
        face_lib_cond.dwFaceDataSize = len(img_data)

        upload_id = self.sdk.NET_DVR_FaceDataUpload(user_id, byref(face_lib_cond))
        if upload_id < 0:
            print("[-] Yuz rasmini yuklashda xatolik:", self.sdk.NET_DVR_GetLastError())
            return False
        else:
            print("[+] Yuz rasm muvaffaqiyatli yuklandi.")
            return True

    def detect_face(self, user_id, channel, timeout=5000):
        face_detect = NET_DVR_FACERECOG_RESULT()
        face_detect.dwSize = sizeof(NET_DVR_FACERECOG_RESULT)
        result = self.sdk.NET_DVR_FaceDetect(user_id, channel, byref(face_detect), timeout)
        if result < 0:
            print("[-] Yuz aniqlashda xatolik:", self.sdk.NET_DVR_GetLastError())
            return None
        else:
            print("[+] Yuz aniqlash muvaffaqiyatli.")
            return face_detect