import pendulum, datetime
import logging, time
from amocrm.v2 import Lead as _Lead, tokens, Contact, Company, Status, filters, custom_field
from fpdf import FPDF
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, dispatcher
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os.path
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text('Привет, по поводу экскурсии пиши @innotravel')
def id(update: Update, context: CallbackContext) -> None:
    """Sends explanation on how to use the bot."""
    update.message.reply_text(update.message.chat_id)

def catch(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        id = int(context.args[0])
        gidd = context.args[1]
        lead = Lead.objects.get(query=id)
        if (lead.gid is None):
            lead.gid = gidd
            for elem in lead._data['custom_fields_values']:
                if (elem['field_id'] == 119783) or (elem['field_id'] == 396957) or (elem['field_id'] == 119781) or (
                        elem['field_id'] == 119779):
                    elem['field_type'] = 'numeric'
                elif((elem['field_id'] == 596561)):
                    elem['field_type'] = 'text'
            lead.status = 'назначен принимающий гид'
            lead._data['custom_fields_values'] = [del_field(elem) if elem['field_type'] == 'select' else elem for elem
                                                  in
                                                  lead._data['custom_fields_values']]

            lead.update()
            cntct = Contact.objects.get(object_id=lead.contacts._data[0]['id'])
            telmail = ""
            for i in cntct._data['custom_fields_values']:
                telmail += i['values'][0]['value'] + " "
            info = "Вы назначены на эту экскурсию.\n" + cntct.name + " " + str(telmail) +"\n"+ str(lead.data_ekskursii) + " " + str(lead.vremia_ekskursii) +"\n" + str(int(lead.kol_vo_detei_do_7)) + " детей, " + str(int(lead.kol_vo_do_18)) + " до 18, " + str(int(lead.kol_vo_vzr)) + " взрослых\n" + str(lead.price) + " руб"
            update.message.reply_text(info)
            day = lead.data_ekskursii[:2]
            mon = lead.data_ekskursii[3:5]
            ye = lead.data_ekskursii[6:10]
            date_begin = pendulum.datetime(int(ye), int(mon), int(day), int(lead.vremia_ekskursii[:2]), int(lead.vremia_ekskursii[3:5]), tz='Europe/Moscow')
            date_end = date_begin.add(minutes=90)
            info = cntct.name + " " + str(telmail) + "Гид: " + str(gidd) +"\n"+ str(lead.data_ekskursii) + " " + str(lead.vremia_ekskursii) +"\n" + str(int(lead.kol_vo_detei_do_7)) + " детей, " + str(int(lead.kol_vo_do_18)) + " до 18, " + str(int(lead.kol_vo_vzr)) + " взрослых\n" + str(lead.price) + " руб"
            event = {
                'summary': 'Экскурсия',
                'location': 'Университет Иннополис',
                'description': info,
                'start': {
                    'dateTime': str(date_begin),
                    'timeZone': 'Europe/Moscow',
                },
                'end': {
                    'dateTime': str(date_end),
                    'timeZone': 'Europe/Moscow',
                },
            }

            event = service.events().insert(calendarId='ge488uhik7rjj44dkbvehaaot4@group.calendar.google.com',
                                            body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        else:
            update.message.reply_text("Уже забрали:(")

        print(lead.name)


    except (IndexError, ValueError):
        update.message.reply_text('Что-то пошло не так. Попробуйте снова')

def spisky(update: Update, context: CallbackContext) -> None:
    tomorrow = pendulum.tomorrow('Europe/Moscow').format('DD.MM')
    leads = Lead.objects.filter(query="списки высланы")
    d = dict()
    s = set()
    for e in leads:
        try:
            print("Смотрим", e.name)
            if not (e.spiski is None):
                print(e.data_ekskursii, e.vremia_ekskursii)
                # date = list(map(int, e.data_ekskursii.split('.')))
                print(e.data_ekskursii[:5], "==", tomorrow)
                if (e.data_ekskursii[:5] == tomorrow):
                    spisok = e.spiski.split(', ')
                    if e.vremia_ekskursii in s:
                        d[e.vremia_ekskursii] += e.spiski.split(', ')
                    else:
                        d[e.vremia_ekskursii] = e.spiski.split(', ')
                        s.add(e.vremia_ekskursii)

        except:
            print("что-то пошло не так в списках")
    s = sorted(s)
    if len(s) == 0:
        updater.bot.send_message(update.message.chat_id, "На завтра индвивдуальных экскурсий нет")
    else:
        generate_pdf(d, s, tomorrow)
        img = open("docs/" + str(tomorrow) + ".pdf", 'rb')
        updater.bot.send_document(update.message.chat_id, img)

def check_none(param):
    if(param is None):
        return 0

def check_kol_none():
    e.kol_vo_do_18 = check_none(e.kol_vo_do_18)
    e.kol_vo_vzr = check_none(e.kol_vo_vzr)
    e.kol_vo_detei_do_7 = check_none(e.kol_vo_detei_do_7)
    e.kol_vo_vsego = check_none(e.kol_vo_vsego)
    # if (e.tip_individ is None):
    #     e.tip_individ.value == "индивидуально"

def make_correct():
    for elem in e._data['custom_fields_values']:
        if (elem['field_id'] == 119783) or (elem['field_id'] == 396957) or (elem['field_id'] == 119781) or (elem['field_id'] == 119779):
            elem['field_type'] = 'numeric'

    e._data['custom_fields_values'] = [del_field(elem) if elem['field_type'] == 'select' else elem for elem in e._data['custom_fields_values']]

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
    fromm = custom_field.BaseCustomField("from", field_id=119711, code="FROM")
    gclientid = custom_field.BaseCustomField("gclientid", field_id=119713, code="GCLIENTID")
    ym_uid = custom_field.BaseCustomField("_ym_uid", field_id=119715, code="_YM_UID")
    ym_counter = custom_field.BaseCustomField("_ym_counter", field_id=119717, code="_YM_COUNTER")
    gclid = custom_field.BaseCustomField("gclid", field_id=119719, code="GCLID")
    yclid = custom_field.BaseCustomField("yclid", field_id=119721, code="YCLID")
    fbclid = custom_field.BaseCustomField("fbclid", field_id=119723, code="FBCLID")
    kol_vo_vzr = custom_field.NumericCustomField("кол-во взрослых", field_id=119779)
    kol_vo_detei_do_7 = custom_field.NumericCustomField("кол-во детей (до 7)", field_id=119781)
    kol_vo_vsego = custom_field.NumericCustomField("кол-во всего", field_id=119783)
    soprovozhdaiushchii = custom_field.TextCustomField("сопровождающий", field_id=119787)
    nomer_tel_soprovod = custom_field.TextCustomField("номер тел. сопровод.", field_id=119789)
    gid = custom_field.TextCustomField("ГИД", field_id=596561)
    class TIP_INDIVID_ENUMS:
        prisoedinius_k_gruppe = custom_field.SelectValue(id=69731, value='присоединюсь к группе')
        individualno = custom_field.SelectValue(id=69733, value='индивидуально')
    tip_individ = custom_field.SelectCustomField("тип индивид.", field_id=129041, enums=TIP_INDIVID_ENUMS)
    kol_vo_do_18 = custom_field.NumericCustomField("кол-во тинейджеров", field_id=396957)
    data_ekskursii = custom_field.TextCustomField("ДАТА экскурсии", field_id=154059)
    vremia_ekskursii = custom_field.TextCustomField("ВРЕМЯ экскурсии", field_id=154061)
    spiski = custom_field.TextCustomField("СПИСКИ", field_id=154203)
    gtimeind = custom_field.TextCustomField("gTimeInd", field_id=344205)
    gtimegroup = custom_field.TextCustomField("gTimeGroup", field_id=344207)

def del_field(x: dict) -> dict:
    x['values'][0].pop('enum_code')
    return x


def generate_pdf(d, s, date):
    print("Делаем")
    pdf = FPDF()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('DejaVu', '', 10)
    header1= "Общество с ограниченной ответственностью “АЛЛЕГРО”"
    header2 = "420500, г.Иннополис, ул. Спортивная, 114-17"
    header3 = "innotravel@mail.ru 8(843)258-44-60"
    pdf.image('logo.png', 130, 8, 50)
    pdf.cell(0, 10, header1, 0, 0.3)
    pdf.cell(0, 0.3, header2, 0, 0.3)
    pdf.cell(0, 10, header3, 0, 0.3)

    dop = "Списки индивидуальных посетителей " + date

    pdf.set_font('DejaVu', '', 12)
    pdf.cell(0, 10,dop , 0, 1)
    i = 1;
    for slot in s:
        pdf.cell(0, 10, "Экскурсия " + str(slot), 0, 1)
        for person in d[slot]:
            pdf.cell(0, 10, str(i) + ". " + person, 0, 1)
            i+=1
        pdf.cell(0, 10, "" , 0, 1)
    pdf.output("docs/" + str(date)+'.pdf', 'F')
    print("сделали")

tokens.default_token_manager(
    client_id="d8c3bf5f-a4a6-43c3-9870-d7ed2f0d3d73",
    client_secret="hSfml6lMz5GViIe4KXM1c1nMTFxwQEYiO0jNvvZYngEz5Yr2HezvSATiFpoYVVom",
    subdomain="innopolistravel",
    redirect_url="https://innopolistravel.com",
    storage=tokens.FileTokensStorage(),  # by default FileTokensStorage
)
tokens.default_token_manager.init(code="def5020018d175eea777503e7928930d6da10839ece5c826405563fbd1bcc4dcdb9e35ebb16d4452b5d0a905e2a8d86b6aeb248e000128178b411e208e42fd3f3b759bc9967a4db6688ee74e7618b667d7709e9575c2346d1038ca30bf200c27db18bb0c04acbd5bc2462713eef81305d9322f43a0b408f081809e45df179146ba1ffeb4f90f6532a52e4fa57d3d8e49cca1239c1118540d9ea1f3868b2c07a11dca6877603064aea38e89f28c8411678a327971ae15f85b43ff26e5165a72dd6679d4744e2ef3216dd66d9edd43ce679e3945f637aef0ad015da6c340015e41050edd184e134584af96895bf43ab8fd0b83335d0a205685e6f52e44e7f40330b31dbc4b51916d26affb5112954be3663449a8425419b013b6ea4eaf95bba460d5b33a3acb9cbf7d386290e5d5f001ff4f86883a495d0018ce9d8be3fb80ee16f3ebc3d916a929ef443db8026fa5728cdd17b9650ef0b4d4086cc3493d61dba5e793811454405d44a179aa74140ea350fcee418638ac95748bbd68c55a2be308d1ee86ac638976932bc78ee88c1f37ce741a982e6c5393c713d3e43c82bc5f269ee818775f694ef4955e3edead81ddde1a816c8cf0c582f13ab8e2c0ceee1d08f43c5a1457", skip_error=False)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

print("START")
#calendar
creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
if os.path.exists('token.json'):
   creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('calendar', 'v3', credentials=creds)
with open("db.json", "r") as read_file:
    data = json.load(read_file)
print(data)
updater = Updater('1708795844:AAHBwps-tV-yWIQtzyv7_qMIcRChfsLCzUk')
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("catch", catch))
dispatcher.add_handler(CommandHandler("id", id))
dispatcher.add_handler(CommandHandler("spisky", spisky))
updater.start_polling()
# print("ждем")
# updater.idle()
# updater.bot.send_message(186570509, "test")
tomorrow_old = pendulum.today('Europe/Moscow').format('DD.MM')
while (True):
    #рассчитываем кол-во, счет и время
    leads = Lead.objects.filter(query="Первый контакт")
    statuses = []
    count = 0
    print(leads)
    for e in leads:
        try:
            check_kol_none()
            e.kol_vo_vsego = str(int(e.kol_vo_do_18) + int(e.kol_vo_detei_do_7) + int(e.kol_vo_vzr))
            make_correct()
            if ((int(e.kol_vo_do_18) + int(e.kol_vo_vzr)) == 1):
                e.price = 1500
            else:
                e.price = int(e.kol_vo_do_18) * 400 + int(e.kol_vo_vzr) * 850
            if not(e.tip_individ is None):
                if (e.tip_individ.value == "индивидуально"):
                    if not (e.vremia_ekskursii is None):
                        print("Время задано")
                    elif (e.gtimeind is None):
                        print("Ошибка")
                    elif (len(str(e.gtimeind)) >= 7):
                        e.vremia_ekskursii = str(e.gtimeind)[:-3]
                elif (e.tip_individ.value == "присоединюсь к группе"):
                    e.vremia_ekskursii = str(e.gtimegroup)
                e.status = 'согласованы дата и время'
                print(e.name + "первый контакт")
                e.update()
        except:
            print("Что-то пошло не так")
            updater.bot.send_message(186570509, "Что-то пошло не так", e.id)

    #рассылаем уведомления и ищем гидов
    leads = Lead.objects.filter(query="согласованы дата и время")
    time.sleep(10)
    for e in leads:
        try:
            cntct = Contact.objects.get(object_id=e.contacts._data[0]['id'])
            if e.tip_individ.value == "индивидуально":
                req = "Новая заявка\n" + "Дата: " + e.data_ekskursii + ", Время: " + e.vremia_ekskursii + "\n" + "индвидуально\n" + "Чтобы взять экскурсию наберите /catch " + str(e.id) + " ИМЯ"
                print(req)
                for guide in data['guides']:
                    try:
                        updater.bot.send_message(guide, req)
                    except:
                        print(guide, 'плохой id')
        except:
            print("Что-то пошло не так")
            updater.bot.send_message(186570509, "Что-то пошло не так", e.id)
    time.sleep(10)
    leads = Lead.objects.filter(query="назначен принимающий гид")
    for e in leads:
        try:
            print("Смотрим", e.name)
            if not (e.spiski is None):
                print("Меняем статус", e.name)
                e.status = 'списки высланы'
                make_correct()
                e.update()
        except:
            print("что-то пошло не так в в переносе из принимающего гида в списки")
    for i in range (0, 4):
        time.sleep(60*15)
        pause = Lead.objects.filter(query="назначен принимающий гид")

updater.idle()


