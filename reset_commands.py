import asyncio
from aiogram import Bot
from aiogram.types import BotCommand

async def reset_commands():
    bot = Bot(token='8253186876:AAFyPFRA1yBHX4VSSL40rLaI7vsjJAOEGNU')
    
    # Удаляем все старые команды
    await bot.delete_my_commands()
    print('✅ Старые команды удалены')
    
    # Устанавливаем новые команды с иконками
    commands = [
        BotCommand(command='start', description='🚀 Запуск'),
        BotCommand(command='menu', description='📋 Меню'),
        BotCommand(command='profile', description='👤 Профиль'),
        BotCommand(command='buy', description='💎 Токены'),
        BotCommand(command='balance', description='💰 Баланс'),
        BotCommand(command='help', description='❓ Помощь'),
        BotCommand(command='support', description='🛠 Поддержка'),
    ]
    
    await bot.set_my_commands(commands)
    print('✅ Новые команды с иконками установлены!')
    print('🟦 СИНЕЕ МЕНЮ ГОТОВО!')
    
    await bot.session.close()

if __name__ == '__main__':
    asyncio.run(reset_commands())