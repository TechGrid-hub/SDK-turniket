def kunlar_soni(yil):
    if (yil % 4 == 0 and yil % 100 != 0) or (yil % 400 == 0):
        return 366  # Kabisa yil
    else:
        return 365  # Oddiy yil

# Foydalanuvchidan yilni olish
yil = int(input("Yilni kiriting: "))
kunlar = kunlar_soni(yil)
print(f"{yil}-yilda {kunlar} kun bor.")
