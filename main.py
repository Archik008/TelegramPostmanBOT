import telebot 
import time
import sqlite3
from telebot import types 


bot = telebot.TeleBot('5902650564:AAH1BHFPzGXB2dn_bYtRcImCIsiNzWdOlLI')
base = sqlite3.connect('base.db', check_same_thread=False)
cursor = base.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    name TEXT,
    id TEXT
)""")
base.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS letters(
    value TEXT,
    fromuser TEXT,
    touser TEXT
)""")
base.commit()


cursor.execute("""CREATE TABLE IF NOT EXISTS bansuper(
    name TEXT,
    id TEXT
)""")
base.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS nicknames(
    name_in_bot TEXT,
    nick TEXT
)""")
base.commit()


def add_nicks(mesg):
    name = ''
    for i in cursor.execute(f"SELECT name FROM users where id = '{mesg.chat.id}'"):
        name += ''.join(i)
        break
    cursor.execute(f"SELECT name_in_bot FROM nicknames WHERE name_in_bot = '{name}'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO nicknames VALUES(?, ?)", (name, mesg.from_user.username))
        base.commit()
    else:
        pass

kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton('Да')
btn2 = types.KeyboardButton('Нет')
kb.add(btn1, btn2)

only_yes = types.ReplyKeyboardMarkup(resize_keyboard=True)
only_yes.add(btn2)

@bot.message_handler(commands=['start'])
def starting(message):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{message.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(message)
        bot.send_message(message.chat.id, 'Здравствуй! Это бот для отправки сообщений(писем) другим пользователям этого бота.Также можно отправлять анонимные письма, не указав в них ваше имя')
        time.sleep(2)
        bot.send_message(message.chat.id, 'Чтобы отправлять письма(сообщения)и просматривать их в этом боте, вам нужно зарегистрироваться введя команду /create_a_mailbox(если вы не зарегистрированы). Введите /help для показа всех команд.')
    else:
        bot.send_message(message.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')

@bot.message_handler(commands=['help'])
def show_list(msg):
    comands = ['/start - запуск бота, или же его перезапуск', 'Чтобы отменить выполнение какой то команды, введите команду /cancel', 'Чтобы посмотреть письма, которые пришли вам в этом боте, понадобится ввести команду /show_letters', 'С помощью команды /write_letter вы отправляете сообщения (письма в данном контексте) другому пользователю', 'Чтобы изменить имя в боте, введите команду /change_mailbox', 'Чтобы посмотреть пользователей, зарегистрированных в этом боте, введите команду /show_mailboes', 'Ну и наконец, /report - команда, чтобы пожаловаться на другого пользователя администратору этого бота', '/clear - очистить все пришедшие вам письма']
    mesg = f"""Список команд:"""
    for i in comands:
        mesg += f"\n{i}"
    bot.send_message(msg.chat.id, mesg)

@bot.message_handler(commands=['create_a_mailbox'])
def creating(message):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{message.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(message)

        cursor.execute(f"SELECT name FROM users WHERE id = '{str(message.chat.id)}'")

        if cursor.fetchone() is None:
            query = bot.send_message(message.chat.id, 'Введите имя для вашего почтового ящика, т.e. введите имя которое будет видно остальным пользователям')
            bot.register_next_step_handler(query, registering)
        else:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
    else:
        bot.send_message(message.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')


def registering(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, 'Действие отменено')
    elif len(message.text) < 3:
        bot.send_message(message.chat.id, 'Слишком короткое имя')
    elif '/' in message.text:
        bot.send_message(message.chat.id, 'Недопустимое имя')
    else:
        cursor.execute(f"SELECT name FROM users WHERE name = '{message.text}'")
        
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users VALUES(?, ?)", (message.text, str(message.chat.id)))
            base.commit()
            bot.send_message(message.chat.id, 'Вы зарегистрированы!')
        else:
            bot.send_message(message.chat.id, 'Такое имя уже занято.')



@bot.message_handler(commands=['change_mailbox'])
def changing(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'")

        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Вы не можете менять ваше имя, так как его у вас нету')
        else:
            if msg.text == '/cancel':
                bot.send_message(msg.chat.id, 'Действие отменено')
            else:
                query =  bot.send_message(msg.chat.id, 'Введите новое имя вашего почтового ящика здесь')
                bot.register_next_step_handler(query, processing_to_change)
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')




def processing_to_change(msg):
    
    if len(msg.text) < 3:
        bot.send_message(msg.chat.id, 'Слишком короткое имя. Введите измененное имя еще раз с помощью команды /change_mailbox')
    elif '/' in msg.text:
        bot.send_message(msg.chat.id, 'Недопустимое имя')
    else:
        cursor.execute(f"SELECT name FROM users WHERE name = '{msg.text}'")
        
        if cursor.fetchone() is None:
            cursor.execute(f"UPDATE users SET name = '{msg.text}' WHERE id = '{msg.chat.id}'")
            base.commit()
            bot.send_message(msg.chat.id, f'Новое имя для почтового ящика здесь: {msg.text}')
        else:
            bot.send_message(msg.chat.id, 'Такое имя уже занято, введите комманду /change_mailbox еще раз')

    

@bot.message_handler(commands=['show_name'])
def showing(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'")

        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'У вас нету имени почтового ящика')
        else:
            for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
                name = ''.join(i)
                bot.send_message(msg.chat.id, f'Ваше имя: <b>{name}</b>', parse_mode='HTML')
                break
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')


@bot.message_handler(commands=['write_letter'])
def writing(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'")
        
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Вы не можете отправлять сообщения, так как у вас нету имени почтового ящика ')
        else:
            vopr = bot.send_message(msg.chat.id, 'Кому вы хотите написать? Выберите пользователя и напишите его имя ниже:')
            arr = []
            mesg = ''
            for i in cursor.execute("SELECT name FROM users"):
                arr.append(''.join(i))
            for i in arr:
                mesg += f"\n{i}"
            quering = bot.reply_to(vopr, mesg)
            bot.register_next_step_handler(quering, to_user)
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')



touser = ''
from_user = ''
val = ''
def to_user(msg):
    global touser
    if msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено')
    else:
        cursor.execute(f"SELECT name FROM users WHERE name = '{msg.text}'")
        
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Нету такого пользователя этого бота')
        else:
            touser = msg.text
            question = """
            Показать адресату (получающему) ваше имя в письме?
            """

            query_from_user = bot.send_message(msg.chat.id, question, reply_markup=kb)
            bot.register_next_step_handler(query_from_user, from_user_letter)

def from_user_letter(message):
    global from_user
    if message.text == '/cancel':
        bot.send_message(message.chat.id, 'Действие отменено')
    else:
        
        if message.text == 'Да':
            from_user = ''
            for i in cursor.execute(f"SELECT name FROM users WHERE id = '{message.chat.id}'"):
                from_user = ''.join(i)
                break
            query =  bot.send_message(message.chat.id, 'Напишите что нибудь(или отправьте голосовое, видео, фото) но не документы', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(query, writing_a_mes)
        else:
            from_user = 'Неизвестно'
            query =  bot.send_message(message.chat.id, 'Напишите что нибудь(или отправьте голосовое, видео, фото) но не документы', reply_markup=types.ReplyKeyboardRemove())
            bot.register_next_step_handler(query, writing_a_mes)

id_file = ''
capt = ''

def writing_a_mes(msg):
    if msg.text == '/cancel':
        global from_user
        global touser

        bot.send_message(msg.chat.id, 'Действие отменено')

        from_user = ''
        touser = ''
    else:
        global val
        global id_file
        global capt
        if msg.content_type == 'photo':
            if msg.caption is None:
                id_file = msg.photo[-1].file_id
                capt = None
            else:
                id_file = msg.photo[-1].file_id
                capt = msg.caption
            bot.send_message(msg.chat.id, 'Имейте ввиду, если отправите сразу несколько фото(или видео, аудио), то отправится только последнее из них. Здесь так не работает')
            time.sleep(2)
            query = bot.send_message(msg.chat.id, 'Отправляем?', reply_markup=kb)
            bot.register_next_step_handler(query, sending_photo)
        elif msg.content_type == 'text':
            val = msg.text
            quest = bot.send_message(msg.chat.id, 'Отправляем?', reply_markup=kb)
            bot.register_next_step_handler(quest, sending_text)
        elif msg.content_type == 'voice':
            id_file = msg.voice.file_id
            question = bot.send_message(msg.chat.id, 'Не хотите сделать подпись в вашем голосовом?(Введите ответ которые отличается от ответа ниже чтобы сделать подпись)', reply_markup=only_yes)
            bot.register_next_step_handler(question, sending_audio)
        elif msg.content_type == 'video':
            id_file = msg.video.file_id
            capt = msg.caption
            vopros = bot.send_message(msg.chat.id, 'Отправляем?', reply_markup=kb)
            bot.register_next_step_handler(vopros, sending_video)
        else:
            bot.send_message(msg.chat.id, 'Неверный тип данных')






def sending_audio(msg):
    global id_file
    global capt
    global from_user
    global touser
    global val
    
    info = []
   
    capt = msg.text if msg.text != 'Нет' else capt 

    info.append('audio')
    info.append(id_file)
    info.append(capt)
    val = '@'.join(info)

    cursor.execute("INSERT INTO letters VALUES(?, ?, ?)", (val, from_user, touser))
    base.commit()

    for i in cursor.execute(f"SELECT id FROM users WHERE name = '{touser}'"):
        id = ''.join(i)
        bot.send_message(int(id), 'У вас новое письмо. Чтобы посмотреть все письма введите команду /show_letters')
        break

    for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
        name = ''.join(i)
        cursor.execute("INSERT INTO uknowns VALUES(?, ?)", (val, name))
        base.commit()

    bot.send_message(msg.chat.id, 'Письмо отправлено', reply_markup=types.ReplyKeyboardRemove())
    

def sending_video(msg):
    global id_file
    global capt
    global from_user
    global touser
    global val
    
    if msg.text == 'Да':
        info = []

        info.append('video')
        info.append(id_file)
        info.append(capt)
        val = '@'.join(info)

        cursor.execute("INSERT INTO letters VALUES(?, ?, ?)", (val, from_user, touser))
        base.commit()

        for i in cursor.execute(f"SELECT id FROM users WHERE name = '{touser}'"):
            id = ''.join(i)
            bot.send_message(int(id), 'У вас новое письмо. Чтобы посмотреть все письма введите команду /show_letters')
            break
        for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
            name = ''.join(i)
            cursor.execute("INSERT INTO uknowns VALUES(?, ?)", (val, name))
            base.commit()


        bot.send_message(msg.chat.id, 'Письмо отправлено', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(msg.chat.id, 'Действие отменено', reply_markup=types.ReplyKeyboardRemove())

        
def sending_photo(msg):
    global id_file
    global capt
    global from_user
    global touser
    global val

    if capt is None:
        capt = ''
    
    if msg.text == 'Да':
        info = []


        info.append('photo')
        info.append(id_file)
        info.append(capt)
        val = '@'.join(info)

        cursor.execute("INSERT INTO letters VALUES(?, ?, ?)", (val, from_user, touser))
        base.commit()

        for i in cursor.execute(f"SELECT id FROM users WHERE name = '{touser}'"):
            id = ''.join(i)
            bot.send_message(int(id), 'У вас новое письмо. Чтобы посмотреть все письма введите команду /show_letters')
            break
        for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
            name = ''.join(i)
            cursor.execute("INSERT INTO uknowns VALUES(?, ?)", (val, name))
            base.commit()


        bot.send_message(msg.chat.id, 'Письмо отправлено', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(msg.chat.id, 'Действие отменено', reply_markup=types.ReplyKeyboardRemove())


def sending_text(msg):
    global touser
    global from_user
    global val

    if msg.text == 'Да':
        cursor.execute("INSERT INTO letters VALUES(?, ?, ?)", (val, from_user, touser))
        base.commit()

        
        for i in cursor.execute(f"SELECT id FROM users WHERE name = '{touser}'"):
            id = ''.join(i)
            bot.send_message(int(id), 'У вас новое письмо. Чтобы посмотреть все письма введите команду /show_letters')
            break

        for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
            name = ''.join(i)
            cursor.execute("INSERT INTO uknowns VALUES(?, ?)", (val, name))
            base.commit()
        
        bot.send_message(msg.chat.id, 'Письмо отправлено', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(msg.chat.id, 'Действие отменено', reply_markup=types.ReplyKeyboardRemove())

    

def delete_data_letters():
    cursor.execute("DELETE FROM letters")
    cursor.execute("DELETE FROM uknowns")
    cursor.execute("DELETE FROM nicknames")
    base.commit()
    print('Данные очищены')


        

@bot.message_handler(commands=['show_letters'])
def showing(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'")
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'У тебя еще нету писем')
        else:
            to_name = ''
            name = ''
            value = []

            for i in cursor.execute(f"SELECT name FROM users where id = '{msg.chat.id}'"):
                name += ''.join(i)
                break

            for i in cursor.execute("SELECT * FROM letters"):
                if name in i[2]:
                    to_name += name
                    break
            
            if len(to_name) == 0:
                bot.send_message(msg.chat.id, 'У тебя еще нету писем')

            else:
                from_user = []

                for i in cursor.execute("SELECT * FROM letters"):
                    if to_name in i[2]:
                        value.append(''.join(i[0]))
                        from_user.append(''.join(i[1]))
                
                for i in range(len(value)):

                    if 'photo' in value[i]:
                        arr = value[i].split('@')
                        get_photo_id = arr[1]
                        photochka = bot.send_photo(msg.chat.id, get_photo_id, caption=arr[2])
                        bot.reply_to(photochka, f"От кого: {from_user[i]}")
                    elif 'audio' in value[i]:
                        arr = value[i].split('@')
                        get_audio_id = arr[1]
                        if 'Nope' in arr:
                            audio = bot.send_audio(msg.chat.id, get_audio_id) 
                            bot.reply_to(audio, f"От кого: {from_user[i]}")
                        else:
                            audio = bot.send_audio(msg.chat.id, get_audio_id, caption=arr[2]) 
                            bot.reply_to(audio, f"От кого: {from_user[i]}")
                    elif 'video' in value[i]:
                        arr = value[i].split('@')
                        get_video_id = arr[1]

                        if len(arr[2]) < 1:
                            audio = bot.send_video(msg.chat.id, get_video_id, caption=arr[2]) 
                            bot.reply_to(audio, f"От кого: {from_user[i]}")
                        else:
                            audio = bot.send_video(msg.chat.id, get_video_id, caption=arr[2]) 
                            bot.reply_to(audio, f"От кого: {from_user[i]}")

                    else:
                        result = f""""""
                        result += f'{value[i]}'
                        result += f'\nОт кого: {from_user[i]}'
                        bot.send_message(msg.chat.id, result)
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')
        

@bot.message_handler(commands=['show_mailboxes'])
def showing_mailboxes(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        result = f"""Все имена почтовых ящиков:"""
        for i in cursor.execute("SELECT name FROM users"):
            names = ''.join(i)
            result += f'\n{names}'
        bot.send_message(msg.chat.id, result)
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')


@bot.message_handler(commands=['report'])
def start_reporting(msg):
    cursor.execute(f"SELECT name FROM bansuper WHERE id = '{msg.chat.id}'")
    if cursor.fetchone() is None:
        add_nicks(msg)

        list_of_reasons = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reason1 = types.KeyboardButton('Спам')
        reason2 = types.KeyboardButton('Оскорбления')
        reason2 = types.KeyboardButton('Травля')
        list_of_reasons.add(reason1, reason2)
        get_reason = bot.send_message(msg.chat.id, 'Укажите причину жалобы')
        bot.register_next_step_handler(get_reason, getting_reason)
    else:
        bot.send_message(msg.chat.id, 'Вы не можете взаимодействовать с ботом, вы забанены')

report = ''
reason = ''

def getting_reason(msg):
    answ = ''
    for i in msg.text:
        answ += i.lower()
    if msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено')
    else:
        global reason
        reason = msg.text
        get_user = f"""На кого вы планируете подать жалобу админу? Список пользователей:"""
        for i in cursor.execute("SELECT name FROM users"):
            names = ''.join(i)
            get_user += f'\n{names}'
        query = bot.send_message(msg.chat.id, get_user, reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query, get_repost_to_admin)
        
some_info = ''

fromuser = ''
def get_repost_to_admin(msg):

    users = []
    for i in cursor.execute("SELECT name FROM users"):
        users.append(''.join(i))
    if msg.text not in users:
        bot.send_message(msg.chat.id, 'Нету такого пользователя бота')
    elif msg.text == 'Admin':
        bot.send_message(msg.chat.id, 'На админа? Ты че?')
    elif msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено')
    else:
        global reason
        global report
        global fromuser
        admin_id = ''
        for i in cursor.execute("SELECT id FROM users WHERE name = 'Admin'"):
            admin_id += ''.join(i)
            break
        for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
            fromuser = ''.join(i)
        report = f"""Жалоба на пользователя {msg.text}. Причина: {reason}."""
        query = bot.send_message(msg.chat.id, 'Добавьте доп. информацию', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(query, FINALLY_REPORT)




def FINALLY_REPORT(msg):
    global report
    global fromuser
    report += f""". Доп инфа:  {msg.text}"""
    cursor.execute("INSERT INTO letters VALUES(?, ?, ?)", (report, fromuser, 'Admin'))
    base.commit()
    for i in cursor.execute(f"SELECT id FROM users WHERE name = 'Admin'"):
        id = ''.join(i)
        bot.send_message(int(id), 'Сэр, у вас новое письмо, жалоба от пользователя')
        break
    bot.send_message(msg.chat.id, 'Жалоба отправлена')
    report = ''
    
admin_id = ''
@bot.message_handler(commands=['enter_as_admin'])
def entering(msg):
    global admin_id

    for i in cursor.execute("SELECT id FROM users WHERE name = 'Admin'"):
        admin_id = ''.join(i)
        break

    if str(msg.chat.id) != admin_id:
        bot.send_message(msg.chat.id, 'Вы не являетесь администратором чата')
    else:
        bot.send_message(msg.chat.id, 'Добро пожаловать!')
        time.sleep(1)
        comands = f"""Команды:"""
        arr_of_cmdns = ['/all_letters - показать все письма юзеров с их именами', '/rassylka - сделать рассылку', '/ban - забанить юзера', '/all_usernames - никнеймы пользователей', '/all_names - все имена пользователей в этом боте', '/razban - разбанить юзера']
        for i in arr_of_cmdns:
            comands += f'\n{i}'
        bot.send_message(msg.chat.id, comands)

@bot.message_handler(commands=['all_letters'])
def showing(msg):
    global admin_id

    for i in cursor.execute("SELECT id FROM users WHERE name = 'Admin'"):
        admin_id = ''.join(i)
        break

    if str(msg.chat.id) != admin_id:
        bot.send_message(msg.chat.id, 'Данная команда принадлежит администратору')
    else:
        lets = []
        for i in cursor.execute("SELECT * FROM letters"):
            lets.append(i)
        if len(lets) < 1:
            bot.send_message(msg.chat.id, 'Нету писем ;(')
        else:
            res = f"""Все письма: """
            for i in cursor.execute("SELECT * FROM letters"):
                part = f"{i[0]}, От: {i[1]}, Кому: {i[2]}"
                res += f"\n{part}"
            bot.send_message(msg.chat.id, res)

@bot.message_handler(commands=['all_usernames'])
def show(msg):
    global admin_id

    for i in cursor.execute("SELECT id FROM users WHERE name = 'Admin'"):
        admin_id = ''.join(i)
        break

    if str(msg.chat.id) != admin_id:
        bot.send_message(msg.chat.id, 'Данная команда принадлежит администратору')
    else:
        mesage = f"""Пользователи:"""
        for i in cursor.execute("SELECT * FROM nicknames"):
            part_of_mesage = f"{i[0]} = {i[1]}"
            mesage += f"\n{part_of_mesage}"
        bot.send_message(msg.chat.id, mesage)

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn_cancel = types.KeyboardButton('Отмена')
keyboard.add(btn_cancel)
@bot.message_handler(commands=['rassylka'])
def rassylanie(msg):
    global admin_id

    for i in cursor.execute("SELECT id FROM users WHERE name = 'Admin'"):
        admin_id = ''.join(i)
        break

    if str(msg.chat.id) != admin_id:
        bot.send_message(msg.chat.id, 'Данная команда принадлежит администратору')
    else:
        if msg.text == '/cancel':
            bot.send_message(msg.chat.id, 'Действие отменено.')
        else:
            query = bot.send_message(msg.chat.id, 'Введите рассылку:')
            bot.register_next_step_handler(query, sending_rassylka)

def sending_rassylka(msg):
    if msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено')
    else:
        rassylka = f"<b>Рассылка</b>\n{msg.text}"
        for i in cursor.execute("SELECT * FROM users"):
            id = ''.join(i[1])
            if 'Admin' in i[0]:
                bot.send_message(msg.chat.id, 'Рассылка выполнена')
            else:
                bot.send_message(int(id), rassylka, parse_mode='HTML')
    
@bot.message_handler(commands=['ban'])
def take_ban(msg):
    vopr = bot.send_message(msg.chat.id, 'Кого вы хотите забанить? Выберите пользователя и напишите его имя ниже:')
    arr = []
    mesg = ''
    for i in cursor.execute("SELECT name FROM users"):
        arr.append(''.join(i))
    for i in arr:
        mesg += f"\n{i}"
    quering = bot.reply_to(vopr, mesg)
    bot.register_next_step_handler(quering, ban_user)

def ban_user(msg):
    if msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено.')
    else:
        cursor.execute(f"SELECT name FROM users WHERE name = '{msg.text}'")
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Нету такого юзера ;(')
        else:
            for i in cursor.execute(f"SELECT id FROM users WHERE name = '{msg.text}'"):
                cursor.execute("INSERT INTO bansuper VALUES(?, ?)", (msg.text, ''.join(i)))
                base.commit()
                bot.send_message(msg.chat.id, 'Юзер забанен')
                break
            for i in cursor.execute(f"SELECT id FROM users WHERE name = '{msg.text}'"):
                id = ''.join(i)
                bot.send_message(int(id), 'Вас забанили и вы не можете теперь взаимодействовать с ботом')
                break

@bot.message_handler(commands=['razban'])
def razbanning(msg):
    if msg.text == '/cancel':
        bot.send_message(msg.chat.id, 'Действие отменено.')
    else:
        vopr = bot.send_message(msg.chat.id, 'Кого вы хотите разбанить? Выберите пользователя и напишите его имя ниже:')
        arr = []
        mesg = ''
        for i in cursor.execute("SELECT name FROM users"):
            arr.append(''.join(i))
        for i in arr:
            mesg += f"\n{i}"
        quering = bot.reply_to(vopr, mesg)
        bot.register_next_step_handler(quering, procesing)

def procesing(msg):
    cursor.execute("SELECT name FROM users")
    if cursor.fetchone() is None:
        bot.send_message(msg.chat.id, 'Нету такого ;(')
    else:
        cursor.execute(f"SELECT name FROM bansuper WHERE name = '{msg.text}'")
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Нету такого в списке забаненных')
        else:
            cursor.execute(f"DELETE FROM bansuper WHERE name = '{msg.text}'")
            base.commit()
            bot.send_message(msg.chat.id, 'Юзер разбанен')
            for i in cursor.execute(f"SELECT id FROM users WHERE name = '{msg.text}'"):
                id = ''.join(i)
                bot.send_message(int(id), 'Вас разбанили')
@bot.message_handler(commands=['clear'])
def clearing(msg):
    query = bot.send_message(msg.chat.id, 'Вы уверены?', reply_markup=kb)
    bot.register_next_step_handler(query, finish_clearing)

def finish_clearing(msg):
    if msg.text == 'Да':
        name = ''
        for i in cursor.execute(f"SELECT name FROM users WHERE id = '{msg.chat.id}'"):
            name += ''.join(i)
            break
        cursor.execute(f"SELECT touser FROM letters WHERE touser = '{name}'")
        if cursor.fetchone() is None:
            bot.send_message(msg.chat.id, 'Нету тебе писем еще', reply_markup=types.ReplyKeyboardRemove())
        else:
            cursor.execute(f"DELETE FROM letters WHERE touser = '{name}'")
            base.commit()
            bot.send_message(msg.chat.id, 'Ваши пришедшие письма удалены', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(msg.chat.id, 'Ну ладно', reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler()
def take_nothing(msg):
    bot.send_message(msg.chat.id, 'Неизвестная команда')

bot.polling()