
from amocrm.v2 import Contact as _Contact
from amocrm.v2 import Company as _Company
from amocrm.v2 import Lead as _Lead
from amocrm.v2 import tokens, custom_field


tokens.default_token_manager(
    client_secret="hSfml6lMz5GViIe4KXM1c1nMTFxwQEYiO0jNvvZYngEz5Yr2HezvSATiFpoYVVom",
    client_id="d8c3bf5f-a4a6-43c3-9870-d7ed2f0d3d73",
    subdomain="innopolistravel",
    redirect_url="https://innopolistravel.com",
    storage=tokens.FileTokensStorage(directory_path="/Users/pavelbaharuev/Desktop/amocrm"),
)
# code = ...
# if code:
#     tokens.default_token_manager.init(code, skip_error=True)



class Contact(_Contact):
    dolzhnost = custom_field.TextCustomField("Должность", field_id=119677, code="POSITION")
    telefon = custom_field.ContactPhoneField("Телефон", field_id=119679, code="PHONE")
    email = custom_field.ContactEmailField("Email", field_id=119681, code="EMAIL")
    polzovatelskoe_soglashenie = custom_field.CheckboxCustomField("Пользовательское соглашение", field_id=126297, code="USER_AGREEMENT")
    instagram = custom_field.UrlCustomField("Instagram", field_id=129731)
    instagram_wz = custom_field.TextCustomField("Instagram (WZ)", field_id=281553)


class Company(_Company):
    telefon = custom_field.ContactPhoneField("Телефон", field_id=119679, code="PHONE")
    email = custom_field.ContactEmailField("Email", field_id=119681, code="EMAIL")
    web = custom_field.UrlCustomField("Web", field_id=119683, code="WEB")
    adres = custom_field.TextAreaCustomField("Адрес", field_id=119685, code="ADDRESS")


class Lead(_Lead):
    utm_content = custom_field.BaseCustomField("utm_content", field_id=119687, code="UTM_CONTENT")
    utm_medium = custom_field.BaseCustomField("utm_medium", field_id=119689, code="UTM_MEDIUM")
    utm_campaign = custom_field.BaseCustomField("utm_campaign", field_id=119691, code="UTM_CAMPAIGN")
    utm_source = custom_field.BaseCustomField("utm_source", field_id=119693, code="UTM_SOURCE")
    utm_term = custom_field.BaseCustomField("utm_term", field_id=119695, code="UTM_TERM")
    utm_referrer = custom_field.BaseCustomField("utm_referrer", field_id=119697, code="UTM_REFERRER")
    roistat = custom_field.BaseCustomField("roistat", field_id=119699, code="ROISTAT")
    openstat_service = custom_field.BaseCustomField("openstat_service", field_id=119703, code="OPENSTAT_SERVICE")
    openstat_campaign = custom_field.BaseCustomField("openstat_campaign", field_id=119705, code="OPENSTAT_CAMPAIGN")
    openstat_ad = custom_field.BaseCustomField("openstat_ad", field_id=119707, code="OPENSTAT_AD")
    openstat_source = custom_field.BaseCustomField("openstat_source", field_id=119709, code="OPENSTAT_SOURCE")
    from = custom_field.BaseCustomField("from", field_id=119711, code="FROM")
    gclientid = custom_field.BaseCustomField("gclientid", field_id=119713, code="GCLIENTID")
    ym_uid = custom_field.BaseCustomField("_ym_uid", field_id=119715, code="_YM_UID")
    ym_counter = custom_field.BaseCustomField("_ym_counter", field_id=119717, code="_YM_COUNTER")
    gclid = custom_field.BaseCustomField("gclid", field_id=119719, code="GCLID")
    yclid = custom_field.BaseCustomField("yclid", field_id=119721, code="YCLID")
    fbclid = custom_field.BaseCustomField("fbclid", field_id=119723, code="FBCLID")
    kol_vo_vzroslykh = custom_field.NumericCustomField("кол-во взрослых", field_id=119779)
    kol_vo_detei_do_seven = custom_field.NumericCustomField("кол-во детей (до 7)", field_id=119781)
    kol_vo_vsego = custom_field.NumericCustomField("кол-во всего", field_id=119783)
    soprovozhdaiushchii = custom_field.TextCustomField("сопровождающий", field_id=119787)
    nomer_tel_soprovod = custom_field.TextCustomField("номер тел. сопровод.", field_id=119789)

    class PRINIMAIUSHCHII_GID_ENUMS:
        polina = custom_field.SelectValue(id=65969, value='Полина')
        pasha = custom_field.SelectValue(id=65971, value='Паша')
        oidinoi = custom_field.SelectValue(id=65973, value='Ойдиной')
        lena = custom_field.SelectValue(id=65975, value='Лена')
        dasha = custom_field.SelectValue(id=65977, value='Даша')
        miloslav = custom_field.SelectValue(id=65979, value='Милослав')
    prinimaiushchii_gid = custom_field.SelectCustomField("принимающий гид", field_id=119791, enums=PRINIMAIUSHCHII_GID_ENUMS)

    class TIP_INDIVID_ENUMS:
        prisoedinius_k_gruppe = custom_field.SelectValue(id=69731, value='присоединюсь к группе')
        individualno = custom_field.SelectValue(id=69733, value='индивидуально')
    tip_individ = custom_field.SelectCustomField("тип индивид.", field_id=129041, enums=TIP_INDIVID_ENUMS)
    kol_vo_do_oneeight = custom_field.TextCustomField("кол-во до 18", field_id=149351)
    data_ekskursii = custom_field.TextCustomField("ДАТА экскурсии", field_id=154059)
    vremia_ekskursii = custom_field.TextCustomField("ВРЕМЯ экскурсии", field_id=154061)
    spiski = custom_field.TextCustomField("СПИСКИ", field_id=154203)
    spiski = custom_field.TextCustomField("списки", field_id=154271)
    gtimeind = custom_field.TextCustomField("gTimeInd", field_id=344205)
    gtimegroup = custom_field.TextCustomField("gTimeGroup", field_id=344207)
