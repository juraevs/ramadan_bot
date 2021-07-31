from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import ParseMode
from de_helper import DBHelper
from conf import TOKEN, DB_NAME
from datetime import datetime, timedelta

BTN_TODAY, BTN_TOMORROW, BTN_SAHARLIK, BTN_IFTAR, BTN_MONTH, BTN_LOCATION = ('Bugun', 'Ertaga', 'Saharlik duosi', 'Iftorlik duosi', 'To\'liq taqvim', 'Shaharni o\'zgartirish')
main_buttons = ReplyKeyboardMarkup([
    [BTN_TODAY, BTN_TOMORROW, BTN_MONTH],
    [BTN_SAHARLIK, BTN_IFTAR],
    [BTN_LOCATION],
], resize_keyboard=True)

STATE_REGION = 1
STATE_CALENDAR = 2

user_region = dict()
db = DBHelper(DB_NAME)

def region_buttons():
    regions = db.get_regions()
    buttons = []
    tmp_b = []
    for region in regions:
        tmp_b.append(InlineKeyboardButton(region['name'], callback_data=region['id']))
        if len(tmp_b) == 2:
            buttons.append(tmp_b)
            tmp_b = []
    return buttons

def start(update, context):
    user = update.message.from_user
    user_region[user.id] = None
    buttons = region_buttons()

    update.message.reply_text(
        f'Assalomu alaykum <b>{user.first_name}!</b> Ramazon oyi muborak bo\'lsin\n \nSizga qaysi shahar bo\'yicha ma\'lumot kerak?',
        reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

    return STATE_REGION

def calendar_today(update, context):
    user_id = update.message.from_user.id
    if not user_region[user_id]:
        return STATE_REGION
    region_id = user_region[user_id]
    region = db.get_region(region_id)
    today = str(datetime.now().date())

    calendar = db.get_calendar_by_region(region_id, today)

    update.message.reply_html('<b>☪️ Ramazon</b> <b>2021</b>\n📍<b>{}</b> vaqti\n \n📅 Bugun <b>{}</b>\n \n🤲 Saharlik: <b>{}</b>\n🤲 Iftorlik: <b>{}</b>'.format(region['name'], today, calendar['fajr'][:5], calendar['maghrib'][:5]))

def calendar_tomorrow(update, context):
    user_id = update.message.from_user.id
    if not user_region[user_id]:
        return STATE_REGION
    region_id = user_region[user_id]
    region = db.get_region(region_id)
    dt = str(datetime.now().date() + timedelta(days=1))

    calendar = db.get_calendar_by_region(region_id, dt)

    update.message.reply_html('<b>☪️ Ramazon</b> <b>2021</b>\n📍<b>{}</b> vaqti\n \n📅 Ertaga <b>{}</b>\n \n🤲 Saharlik: <b>{}</b>\n🤲 Iftorlik: <b>{}</b>'.format(region['name'], dt, calendar['fajr'][:5], calendar['maghrib'][:5]))

def calendar_month(update, context):
    user_id = update.message.from_user.id
    if not user_region[user_id]:
        return STATE_REGION
    region_id = user_region[user_id]
    region = db.get_region(region_id)
    photo_path = 'img/region_{}.jpg'.format(region['id'])
    message='<b>Ramazon</b> 2️⃣0️⃣2️⃣1️⃣\n<b>{}</b> vaqti\n '.format(region['name'])
    update.message.reply_photo(photo=open(photo_path, 'rb'), caption=message, parse_mode='HTML',
                               reply_markup=main_buttons)

def saharlik(update, context):
    sahar = "نَوَيْتُ أَنْ أَصُومَ صَوْمَ شَهْرَ رَمَضَانَ مِنَ الْفَجْرِ إِلَى الْمَغْرِبِ، خَالِصًا لِلهِ تَعَالَى أَللهُ أَكْبَر\nُ\nNavaytu an asuvma sovma shahri ramazona minal fajri ilal mag‘ribi, xolisan lillahi taʼaalaa Allohu akbar.\n\nMaʼnosi: Ramazon oyining ro‘zasini subhdan to kun botguncha tutmoqni niyat qildim. Xolis Alloh uchun Alloh buyukdir."
    update.message.reply_text('<b>Saharlik duosi:</b>\n\n{}'.format(sahar),parse_mode=ParseMode.HTML)

def iftar(update, context):
    sahar = 'اَللَّهُمَّ لَكَ صُمْتُ وَ بِكَ آمَنْتُ وَ عَلَيْكَ تَوَكَّلْتُ وَ عَلَى رِزْقِكَ أَفْتَرْتُ، فَغْفِرْلِى مَا قَدَّمْتُ وَ مَا أَخَّرْتُ بِرَحْمَتِكَ يَا أَرْحَمَ الرَّاحِمِينَ\n\nAllohumma laka sumtu va bika aamantu va aʼlayka tavakkaltu va aʼlaa rizqika aftartu, fag‘firliy ma qoddamtu va maa axxortu birohmatika yaa arhamar roohimiyn.\n\nMaʼnosi: Ey Alloh, ushbu Ro‘zamni Sen uchun tutdim va Senga iymon keltirdim va Senga tavakkal qildim va bergan rizqing bilan iftor qildim. Ey mehribonlarning eng mehriboni, mening avvalgi va keyingi gunohlarimni mag‘firat qilgil.'
    update.message.reply_text('<b>Iftorlik duosi:</b>\n\n{}'.format(sahar),parse_mode=ParseMode.HTML)

def location(update, context):
    buttons = region_buttons()

    update.message.reply_text('Sizga qaysi shahar bo\'yicha ma\'lumot kerak?',
        reply_markup=InlineKeyboardMarkup(buttons))
    return STATE_REGION

def inline_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    user_region[user_id] = int(query.data)
    query.message.delete()
    query.message.reply_html(text='<b>Ramazon taqvimi </b> \nQuyidagilardan birini tanlang', reply_markup=main_buttons)

    return STATE_CALENDAR

def main():
    # Updaterni o'rnatish
    updater = Updater(TOKEN, use_context=True)

    # Dispatcher eventlarni aniqlash
    dispatcher = updater.dispatcher

    # start komandasini ushlab qolish
    # dispatcher.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_REGION: [CallbackQueryHandler(inline_callback),
                           MessageHandler(Filters.regex('^(' + BTN_TODAY + ')$'), calendar_today),
                           MessageHandler(Filters.regex('^(' + BTN_TOMORROW + ')$'), calendar_tomorrow),
                           MessageHandler(Filters.regex('^(' + BTN_MONTH + ')$'), calendar_month),
                           MessageHandler(Filters.regex('^(' + BTN_SAHARLIK + ')$'), saharlik),
                           MessageHandler(Filters.regex('^(' + BTN_IFTAR + ')$'), iftar),
                           MessageHandler(Filters.regex('^(' + BTN_LOCATION + ')$'), location)
                           ],
            STATE_CALENDAR:[
                MessageHandler(Filters.regex('^('+BTN_TODAY+')$'), calendar_today),
                MessageHandler(Filters.regex('^('+BTN_TOMORROW + ')$'), calendar_tomorrow),
                MessageHandler(Filters.regex('^('+BTN_MONTH + ')$'), calendar_month),
                MessageHandler(Filters.regex('^('+BTN_SAHARLIK + ')$'), saharlik),
                MessageHandler(Filters.regex('^('+BTN_IFTAR + ')$'), iftar),
                MessageHandler(Filters.regex('^('+BTN_LOCATION + ')$'), location)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    # inline button query
    # dispatcher.add_handler(CallbackQueryHandler(inline_callback))

    updater.start_polling()
    updater.idle()


main()
