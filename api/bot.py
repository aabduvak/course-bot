import logging
import requests

from django.conf import settings
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = settings.TELEGRAM_TOKEN

MENU_ITEMS = {
    'course': '',
    'detail': '',
    'menu': '',
}

def start(update: Update, context):
    start = requests.get('http://localhost:8000/api/getcontent/', params={"title": "start"}).json()
    
    
    url = 'http://localhost:8000/api/getuser/'
    response = requests.get(url, params={'chat_id': update.effective_chat.id})
    
    text = f'{start["text"]} {update.effective_user.first_name}'
        
    update.message.reply_text(text)
    
    if response.status_code != 200:
        register(update, context)
    else:
        welcome(update, context)

def register(update: Update, context):
    registration = requests.get('http://localhost:8000/api/getcontent/', params={"title": "registration"}).json()
    
    button = [
        [KeyboardButton(text=f'{registration["buttons"][0]}', request_contact=True)]
    ]
    
    update.message.reply_text(
        text=registration['text'],
        reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True, one_time_keyboard=True)
    )
    
def send_data(update: Update, context):        
    
    data = {
        'telegram_id': update.effective_user.id,
        'username': update.effective_user.name,
        'first_name': update.effective_user.first_name,
        'last_name': update.effective_user.last_name,
        'chat_id': update.effective_chat.id,
        'link': update.effective_user.link,
        'phone': update.effective_message.contact.phone_number
    }
    
    res = requests.post('http://localhost:8000/api/storeuser/', data=data)
    
    if res.status_code == 200 or res.status_code == 201:
        update.message.reply_text('✅ Рўйҳатдан ўтдингиз')
    else:
        update.message.reply_text('❌ Кутилмаган муаммо содир бўлди')
        return ConversationHandler.END
    
    welcome(update, context)

def welcome(update: Update, context):
    welcome = requests.get('http://localhost:8000/api/getcontent/', params={"title": "welcome"}).json()
    
    buttons = []
    for button in welcome['buttons']:
        buttons.append([KeyboardButton(button)])
    
    MENU_ITEMS['course'] = welcome['buttons'][0]
    MENU_ITEMS['detail'] = welcome['buttons'][1]
    
    update.message.reply_text(text=welcome['text'], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END

def menu(update: Update, context):
    menu = requests.get('http://localhost:8000/api/getcontent/', params={"title": "menu"}).json()
    
    buttons = []
    for button in menu['buttons']:
        buttons.append([KeyboardButton(button)])
    
    MENU_ITEMS['course'] = menu['buttons'][0]
    MENU_ITEMS['detail'] = menu['buttons'][1]
    
    update.message.reply_text(text=menu['text'], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True))
    return ConversationHandler.END

def detail(update: Update, context):
    detail_content = requests.get('http://localhost:8000/api/getcontent/', params={'title': 'detail'}).json()
    
    MENU_ITEMS['menu'] = detail_content['buttons'][0]
    update.message.reply_text(text=detail_content['text'], reply_markup=ReplyKeyboardMarkup([[KeyboardButton(detail_content['buttons'][0])]], resize_keyboard=True, one_time_keyboard=True))
    
    requests.post('http://localhost:8000/api/detail/', json={'telegram_id': update.effective_chat.id})
    
    return ConversationHandler.END
    
def get_products(update: Update, context):
    product_list = requests.get('http://localhost:8000/api/getproducts/').json()
    
    buttons = []
    for product in product_list['items']:
        buttons.append(InlineKeyboardButton(text=product['name'], callback_data=f"product:{product['id']}:status:show"))
    
    content = requests.get('http://localhost:8000/api/getcontent/', params={'title': 'products'}).json()
    update.message.reply_text(text=content['text'], reply_markup=InlineKeyboardMarkup([buttons]))
    return ConversationHandler.END

def button_click(update: Update, context):
    if MENU_ITEMS['course'] == update.message.text:
        get_products(update, context)
    elif MENU_ITEMS['detail'] == update.message.text:
        detail(update, context)
    elif MENU_ITEMS['menu'] == update.message.text:
        menu(update, context)
    #elif update.message.text == 'Тўлов қилиш':
    #    pass
    #elif update.message.text == 'Орқага':
    #    get_products(update, context)

def button_callback(update: Update, context):
    query = update.callback_query
    button_data = query.data.split(':')
    
    if button_data[1] != '0' and button_data[3] == 'show':    
        product = requests.get('http://localhost:8000/api/productdetails/', params={'product_id': button_data[1]}).json()
        
        text = f"{product['id']}. {product['name']}\n\n{product['description']}\n\nКурс нархи {product['price']} сум"
        buttons = [
            InlineKeyboardButton('Тўлов қилиш', callback_data=f"product:{product['id']}:status:payment"),
            InlineKeyboardButton('Орқага', callback_data=f"product:0:status:cancel")
        ]
        
        query.answer('Курс ҳақида маълумотлар')
        query.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=InlineKeyboardMarkup([buttons]))        
    elif button_data[3] == 'cancel':
        query.answer('Орқага')
        return ConversationHandler.END

    elif button_data[3] == 'payment':
        requests.post('http://localhost:8000/api/createdeal/', json={'telegram_id': update.effective_chat.id, 'product_id': button_data[1]}).json()
        
        content = requests.get('http://localhost:8000/api/getcontent/', params={'title': 'payment'}).json()        
        query.answer('Тўлов қилиш')
        query.bot.send_message(chat_id=query.message.chat_id, text=content['text'])
    else:
        query.answer('Нотўғри буйруқ')
        query.bot.send_message(chat_id=query.message.chat_id, text='Нотўғри буйруқ')

def send_files(update: Update, context):
    message = update.effective_message
    deal = requests.get('http://localhost:8000/api/getdeal/', params={"telegram_id": update.effective_chat.id}).json()
    
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        
        file_path = context.bot.get_file(file_id).file_path
    elif message.document:
        document = message.document
        file_id = document.file_id
        file_path = context.bot.get_file(file_id).file_path
    
    if 'error' not in deal:
        requests.post('http://localhost:8000/api/sendfile/', json={'path': file_path, 'deal': deal['deal']}).json()
        
        valid_file = requests.get('http://localhost:8000/api/getcontent/', params={'title': 'valid file'}).json()
        update.message.reply_text(text=valid_file['text'])
    else:
        invalid_file = requests.get('http://localhost:8000/api/getcontent/', params={'title': 'invalid file'}).json()        
        update.message.reply_text(text=invalid_file['text'])
        get_products(update, context)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    contact_handler = MessageHandler(Filters.contact, send_data)
    menu_handler = CommandHandler('menu', menu)
    button_handler = MessageHandler(Filters.text, button_click)
    callback_handler = CallbackQueryHandler(button_callback)
    
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(contact_handler)
    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(button_handler)
    dispatcher.add_handler(callback_handler)
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, send_files))

    updater.start_polling()
    updater.idle()