import telebot
import sqlite3
from telebot import types

BOT_TOKEN = '7514409049:AAHPVlis3DB9Wq0jQxy499dB7yIdce2vFgQ' # Замените на ваш токен

bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect('notes.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        text TEXT
    )
''')
conn.commit()
conn.close()

def get_notes(user_id):
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM notes WHERE user_id = ?", (user_id,))
    notes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return notes

def create_note(message, name, text):
    user_id = message.from_user.id
    try:
        conn = sqlite3.connect('notes.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (user_id, name, text) VALUES (?, ?, ?)", (user_id, name, text))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Заметка '{name}' создана.")
    except sqlite3.IntegrityError:
        bot.reply_to(message, f"⚠️ Заметка с именем '{name}' уже существует для этого пользователя.")

def read_note(message):
    user_id = message.from_user.id
    name = message.text
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM notes WHERE user_id = ? AND name = ?", (user_id, name))
    result = cursor.fetchone()
    conn.close()
    if result:
        bot.reply_to(message, f"📖 Заметка '{name}':\n{result[0]}")
    else:
        bot.reply_to(message, f"⚠️ Заметка '{name}' не найдена.")

def delete_note(message):
    user_id = message.from_user.id
    name = message.text
    conn = sqlite3.connect('notes.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE user_id = ? AND name = ?", (user_id, name))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"🗑️ Заметка '{name}' удалена.")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('Создать заметку 📝'), types.KeyboardButton('Прочитать заметку 📖'), types.KeyboardButton('Удалить заметку 🗑️'))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Создать заметку 📝')
def create(message):
    bot.reply_to(message, "Введите имя заметки:")
    bot.register_next_step_handler(message, process_create_name)

def process_create_name(message):
    name = message.text
    bot.reply_to(message, "Введите текст заметки:")
    bot.register_next_step_handler(message, lambda m: create_note(m, name, m.text))

@bot.message_handler(func=lambda message: message.text == 'Прочитать заметку 📖')
def read(message):
    notes = get_notes(message.from_user.id)
    if notes:
        bot.reply_to(message, f"Список заметок:\n{chr(10).join(notes)}\nВведите имя заметки для чтения:")
        bot.register_next_step_handler(message, read_note)
    else:
        bot.reply_to(message, "Заметок нет.")

@bot.message_handler(func=lambda message: message.text == 'Удалить заметку 🗑️')
def delete(message):
    notes = get_notes(message.from_user.id)
    if notes:
        bot.reply_to(message, f"Список заметок:\n{chr(10).join(notes)}\nВведите имя заметки для удаления:")
        bot.register_next_step_handler(message, delete_note)
    else:
        bot.reply_to(message, "Заметок нет.")

bot.infinity_polling()