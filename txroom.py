token_bot = "8382768846:AAFZVkS1Srf7kIar_M74WfqwbUPY72uPaLU"
CHAT_ID = -1002936567220  
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import ChatPermissions
from telegram.error import NetworkError, TimedOut, RetryAfter, BadRequest, Forbidden
import asyncio, json, requests, base64, logging, threading, re, random, httpx,sqlite3,datauser
from time import sleep
from telegram.ext import JobQueue
from telegram.request import HTTPXRequest
database=datauser.Database("txroom.db")
def quy_doi(sotien):
  return '{:,.0f}'.format(int(sotien)).replace(',', '.')
def tinh_phan_tram(phan_tram, so):
  return round((phan_tram / 100) * so)

def check_int(so):
  if "." in str(so):
    return False
  try:
    x=int(so)*2
    return True
  except:
    return False
async def safe_set_permissions(bot, chat_id, permissions, max_retries=10):
  for attempt in range(max_retries):
    try:
      return await bot.set_chat_permissions(chat_id=chat_id, permissions=permissions)
    except (NetworkError, TimedOut) as e:
      if attempt < max_retries - 1:
        await asyncio.sleep(2 ** attempt)
      else:
        return None 
    except Exception as e:
      return None
      
async def safe_send_dice(bot, chat_id, emoji="🎲", max_retries=10):
  for attempt in range(max_retries):
    try:
      return await bot.send_dice(chat_id=chat_id, emoji=emoji)
    except (NetworkError, TimedOut) as e:
      if attempt < max_retries - 1:
        await asyncio.sleep(2 ** attempt)
    except RetryAfter as e:
      await asyncio.sleep(e.retry_after)
      return await bot.send_dice(chat_id=chat_id, emoji=emoji)
    except Exception as e:
      pass

async def safe_send_message(bot, chat_id, text, parse_mode="HTML", max_retries=10):
  for attempt in range(max_retries):
    try:
      return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except (NetworkError, TimedOut) as e:
      if attempt < max_retries - 1:
        await asyncio.sleep(2 ** attempt)
    except RetryAfter as e:
      await asyncio.sleep(e.retry_after)
      return await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
    except Exception as e:
      pass

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
  print(f"Error occurred: {context.error}")
  if isinstance(context.error, RetryAfter):
    print(f"Rate limited. Waiting {context.error.retry_after} seconds")
    await asyncio.sleep(context.error.retry_after)
  elif isinstance(context.error, TimedOut):
    print("Request timed out")
  elif isinstance(context.error, NetworkError):
    print(f"Network error occurred: {context.error}")
  elif isinstance(context.error, Forbidden):
    print("Bot was blocked by user or removed from group")
  elif isinstance(context.error, BadRequest):
    print(f"Bad request: {context.error}")
async def background_task(application: Application):
  while True:
    await safe_set_permissions(application.bot,chat_id=CHAT_ID,permissions=ChatPermissions(can_send_messages=True,can_send_voice_notes=True,can_send_photos=True,can_invite_users=True))
    getv=database.get_home_data()
    database.update_home(phien_hien_tai=str(int(getv['phien_hien_tai'])+1),trang_thai="waitcai",tong_bet_xiu="0",tong_bet_tai="0")
    message = await safe_send_message(application.bot,chat_id=CHAT_ID,text=f"""🥷 <b>Chơi ẩn danh:</b> Chat riêng bot <a href="https://t.me/txroom_tubaoduong_bot">Tại đây</a>\n\n🚨<b> Phiên mới sắp bắt đầu ! </b>🚨\n💰 Hũ hiện tại: {quy_doi(getv['hu_coin'])} ₫\n\n🎮<b> Cách chơi:</b>\n👉 Đặt Tài: Nhập T [số tiền]\n👉 Đặt Xỉu: Nhập X [số tiền]\n(Ví dụ: T 10000 hoặc X 10000)""",parse_mode="HTML")
    message = await safe_send_message(application.bot,chat_id=CHAT_ID,text=f"👑 PHIÊN [<code>{int(getv['phien_hien_tai'])+1}</code>] ĐANG CHỌN CÁI 👑\n\n⏳ Còn 19 giây để chọn CÁI \n\n🔮 Trạng thái: Hết thời gian không ai chọn cái, admin sẽ tự nhận cái\n\n👉 Lệnh nhanh:\n✅ /lamcai – Lệch cửa 1M\n✅ /lamcai (số tiền) – Lệch tùy chọn (≥1M)\n✅ /lamcai allin – Dùng toàn bộ số dư\n\n⚠️ Khi làm CÁI hệ thống sẽ tạm giữ số tiền tương ứng\n\n💰 Hũ hiện tại: {quy_doi(getv['hu_coin'])} ₫",parse_mode="HTML")
    await asyncio.sleep(19)
    database.update_home(trang_thai="waitbet")
    await asyncio.sleep(1.5)
    get_phien_hien_tai=database.get_home_data()
    check_cai=database.get_phien_cai(get_phien_hien_tai['phien_hien_tai'])
    if check_cai == []:
      await safe_send_message(application.bot,chat_id=CHAT_ID,text="🤖 BOT SẼ TỰ ĐỘNG LÀM CÁI 👑",parse_mode="HTML")
      database.update_home(so_du_cai="5000000",cai="83861412")
    else:
      max_value = max(int(item[1]) for item in check_cai)
      all_max_items = [item for item in check_cai if int(item[1]) == max_value]
      cai_chon = random.sample(all_max_items, 1)
      loai_cai = [item for item in check_cai if item not in cai_chon]
      database.update_home(so_du_cai=cai_chon[0][1],cai=cai_chon[0][0])
      for i in loai_cai:
        so_coin_hien_tai=int(database.get_user_data(i[0])[1])+int(i[1])
        database.update_user(i[0],"coin",str(so_coin_hien_tai))
      await safe_send_message(application.bot,chat_id=CHAT_ID,text=f"👤 NGƯỜI CHƠI {cai_chon[0][0][:-4]}**** ĐƯỢC CHỌN LÀM CÁI 👑",parse_mode="HTML")
    countdown_times = [99, 89, 79, 69, 59, 49, 39, 29, 19, 9]
    #countdown_times=[30,20,10] 
    tien_cai=database.get_home_data()['so_du_cai']
    hu_coin=database.get_home_data()['hu_coin']
    list_cau=database.get_lich_su_phien()
    text_cau = "".join("⚫️" if i[2] == "T" else "⚪️" for i in list_cau)
    for i in countdown_times:
      datang=database.get_phien_cuoc(get_phien_hien_tai['phien_hien_tai'])
      count_T = sum(1 for item in datang if item[1] == 'T')
      count_X = sum(1 for item in datang if item[1] == 'X')
      text=f"⚜️ Phiên [{get_phien_hien_tai['phien_hien_tai']}] Còn {i}s để cược ⏳\n\n💰 Tiền cái {quy_doi(tien_cai)} ₫\n\n⚫️ Cửa Tài: {count_T} người đặt. Tổng tiền {quy_doi(database.get_home_data()['tong_bet_tai'])} ₫ \n⚪️ Cửa Xỉu: {count_X} người đặt. Tổng tiền {quy_doi(database.get_home_data()['tong_bet_xiu'])} ₫\n\n🏦 Hũ hiện tại: {quy_doi(hu_coin)} ₫\n\n📊 Kết quả 12 phiên gần nhất\n{text_cau}"
      await safe_send_message(application.bot,chat_id=CHAT_ID,text=text,parse_mode="HTML")
      await asyncio.sleep(10)
    database.update_home(trang_thai="waitkq")
    await safe_set_permissions(application.bot,chat_id=CHAT_ID,permissions=ChatPermissions(can_send_messages=False,can_send_voice_notes=False,can_send_photos=False,))
    await asyncio.sleep(3)
    datang=database.get_phien_cuoc(get_phien_hien_tai['phien_hien_tai'])
    count_T = sum(1 for item in datang if item[1] == 'T')
    count_X = sum(1 for item in datang if item[1] == 'X')
    message = await safe_send_message(application.bot,chat_id=CHAT_ID,text=f"⌛ Hết thời gian đặt cược! \n\n⚫️ Cửa TÀI: {count_T} người đặt. Tổng tiền {quy_doi(database.get_home_data()['tong_bet_tai'])} ₫ \n⚪️ Cửa XỈU: {count_X} người đặt. Tổng tiền {quy_doi(database.get_home_data()['tong_bet_xiu'])} ₫\n\n🎲🎲🎲 BOT CHUẨN BỊ TUNG XÚC XẮC 🎲🎲🎲",parse_mode="HTML")
    alldice = []
    await asyncio.sleep(2)
    for i in range(3):
      message = await safe_send_dice(application.bot, chat_id=CHAT_ID, emoji="🎲")
      dice_value = message.dice.value
      alldice.append(dice_value)
      await asyncio.sleep(0.75)
    datadice = {"dice1": alldice[0],"dice2": alldice[1], "dice3": alldice[2],"diceall": alldice[0] + alldice[1] + alldice[2]}
    kqdice="T" if datadice['diceall'] >= 11 else "X"
    await asyncio.sleep(2)
    kqend=database.get_phien_cuoc(get_phien_hien_tai['phien_hien_tai'])
    list_win=[]
    for i in kqend:
      rank=int(database.get_user_data(i[0])[2])+int(i[2])
      database.update_user(i[0],"rank",str(rank))
      if int(database.get_user_data(i[0])[3]) > 0:
        t_nap=int(database.get_user_data(i[0])[3])-int(i[2])
        database.update_user(i[0],"tong_nap",str(t_nap))
      if i[1] == kqdice:
        tien_nhan=round(float(i[2])*float(1.9))
        list_win.append((i[0],tien_nhan))
        so_du_hien_tai=int(database.get_user_data(i[0])[1])+tien_nhan
        database.update_user(i[0],"coin",str(so_du_hien_tai))
        await asyncio.sleep(0.075)
    await asyncio.sleep(1)
    text_win = sorted(list_win, key=lambda x: x[1], reverse=True)
    full_dice="XỈU ⚪️" if kqdice =="X" else "TÀI ⚫️"
    text=f"📝 Kết quả cược phiên: \n[{get_phien_hien_tai['phien_hien_tai']}]\n\n🎉 Cửa thắng: {full_dice}\nTOP - ID - Tiền thắng\n"
    for index, value in enumerate(text_win):
      text+=f"{index+1} - {value[0][:-4]}**** - {quy_doi(value[1])} ₫\n"
    await safe_send_message(application.bot,chat_id=CHAT_ID,text=text,parse_mode="HTML")
    await asyncio.sleep(1.5)
    x=int(database.get_home_data()["tong_bet_tai"])
    y=int(database.get_home_data()["tong_bet_xiu"])
    xandy=x+y
    hu_hien_tai=int(database.get_home_data()["hu_coin"])+tinh_phan_tram(5,x+y)
    database.update_home(hu_coin=str(hu_hien_tai))
    if kqdice=="T":
      tien_cuoc_cai=int(database.get_home_data()["so_du_cai"])-int(x)
      tien_cuoc_cai+=round(int(y)*float(0.9))
    else:
      tien_cuoc_cai=int(database.get_home_data()["so_du_cai"])-int(y)
      tien_cuoc_cai+=round(int(x)*float(0.9))
      
    uid_cai=database.get_home_data()['cai']
    so_du_cuoi=int(database.get_user_data(uid_cai)[1])+tien_cuoc_cai
    database.update_user(uid_cai,'coin',str(so_du_cuoi))
    database.add_lich_su_phien(str(y),str(x),kqdice,get_phien_hien_tai['phien_hien_tai'])
    #datadice["diceall"]=3
    if datadice['diceall'] == 3 or datadice['diceall'] == 18:
      if kqend != []:
        so_tien_trong_hu=int(database.get_home_data()["hu_coin"])
        so_tien_no_hu=tinh_phan_tram(80,so_tien_trong_hu)
        hu_moi=(so_tien_trong_hu-so_tien_no_hu)+500000
        database.update_home(hu_coin=str(hu_moi))
        so_tien_cai_an=tinh_phan_tram(30,so_tien_no_hu)
        so_tien_chia=so_tien_no_hu-so_tien_cai_an
        text=f"💥 Nổ hũ phiên: [{get_phien_hien_tai['phien_hien_tai']}],tổng tiền nổ hũ {quy_doi(so_tien_no_hu)} ₫\nTOP - ID - Tiền Thắng Nổ hũ\n"
        if datadice['diceall'] == 3:
          tong_bet_chia=int(database.get_home_data()["tong_bet_xiu"])
        else:
          tong_bet_chia=int(database.get_home_data()["tong_bet_tai"])
        list_no=[]
        for i in kqend:
          if i[1] == kqdice and tong_bet_chia>0:
            tien_cuoc=int(i[2])/tong_bet_chia
            tien_nhan_no=round(so_tien_chia*tien_cuoc)
            list_no.append((i[0],tien_nhan_no))
            so_du_hien_tai=int(database.get_user_data(i[0])[1])+tien_nhan_no
            database.update_user(i[0],"coin",str(so_du_hien_tai))
        if list_no==[]:
          so_tien_cai_an=round(so_tien_cai_an+so_tien_chia)
          text+=f"0 - {database.get_home_data()['cai'][:-4]}**** - {quy_doi(so_tien_cai_an)} ₫\n"
        else:
          text+=f"0 - {database.get_home_data()['cai'][:-4]}**** - {quy_doi(so_tien_cai_an)} ₫\n"
          text_no = sorted(list_no, key=lambda x: x[1], reverse=True)
          for index, value in enumerate(text_no):
            text+=f"{index+1} - {value[0][:-4]}**** - {quy_doi(value[1])} ₫\n"
        so_du_cuoi=int(database.get_user_data(uid_cai)[1])+so_tien_cai_an
        database.update_user(uid_cai,'coin',str(so_du_cuoi))
        await safe_send_message(application.bot,chat_id=CHAT_ID,text=text,parse_mode="HTML")
            
            
            
    database.update_home(cai="0",so_du_cai="0",tong_bet_xiu="0",tong_bet_tai="0")


async def post_init(application: Application):
  await application.bot.send_message(chat_id=CHAT_ID,text="🤖 Bot đã khởi động thành công!")
  asyncio.create_task(background_task(application))
  
async def lamcai(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  if database.get_home_data()['trang_thai'] != "waitcai":
    await update.message.reply_text("Đã hết thời gian chọn làm cái !!!",parse_mode="HTML")
    return
  check_cai_duyet=database.get_phien_cai(database.get_home_data()['phien_hien_tai'],user)
  if check_cai_duyet != []:
    await update.message.reply_text("Bạn đã đăng ký thành công phiên này vui lòng chờ giây lát ",parse_mode="HTML")
    return
  if len(text)==1:
    check_user=database.get_user_data(user)
    soducai=int(check_user[1])
    if soducai < 1000000:
      await update.message.reply_text("Số dư tối thiểu không đủ để làm cái !!!",parse_mode="HTML")
    else:
      soducai=int(database.get_user_data(user)[1])-1000000
      database.update_user(user,"coin",str(soducai))
      database.add_phien_cai(user,"1000000",database.get_home_data()['phien_hien_tai'])
      await update.message.reply_text("Đăng ký danh sách làm cái 1.000.000 ₫ thành công !!",parse_mode="HTML")
  elif len(text)==2:
    lenhorcoin=text[1]
    if lenhorcoin == "allin":
      soducai=int(database.get_user_data(user)[1])
      if soducai < 1000000:
        await update.message.reply_text("Số dư tối thiểu không đủ để làm cái !!!",parse_mode="HTML")
      else:
        database.update_user(user,"coin","0")
        database.add_phien_cai(user,str(soducai),database.get_home_data()['phien_hien_tai'])
        await update.message.reply_text(f"Đăng ký danh sách làm cái {quy_doi(soducai)} ₫ thành công !",parse_mode="HTML")
    else:
      try:
        soducai=int(lenhorcoin)
        if soducai < 1000000:
          await update.message.reply_text("Vui lòng chọn cái với số tiền ≥1M ",parse_mode="HTML")
        elif soducai > int(database.get_user_data(user)[1]):
          await update.message.reply_text("Số dư tài khoản không đủ ",parse_mode="HTML")
        else:
          coinn=int(database.get_user_data(user)[1])-soducai
          database.update_user(user,'coin',str(coinn))
          database.add_phien_cai(user,str(soducai),database.get_home_data()['phien_hien_tai'])
          await update.message.reply_text(f"Đăng ký danh sách làm cái {quy_doi(soducai)} ₫ thành công !",parse_mode="HTML")
      except:
        await update.message.reply_text("Vui lòng sử dụng đúng lệnh /lamcai ",parse_mode="HTML")
  else:
    await update.message.reply_text("Vui lòng sử dụng đúng lệnh /lamcai ",parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = str(update.effective_user.id)
  text = update.message.text.split()
  uid_chat=update.message.chat.id
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  if len(text)==2:
    bet_cua,so_bet=text[0].upper(),text[1]
    if bet_cua in ["T","X"] and check_int(so_bet) != False:
      check_status=database.get_home_data()["trang_thai"]
      if check_status != "waitbet":
        await update.message.reply_text("Hết thời gian đặt cược ! ",parse_mode="HTML")
        return
      if database.get_home_data()['cai'] == user:
        await update.message.reply_text("Bạn đang làm cái không thể cược",parse_mode="HTML")
        return
      if int(so_bet) < 1000:
        await update.message.reply_text("Tiền cược quá bé ! ",parse_mode="HTML")
        return
      soduc=int(database.get_user_data(user)[1])
      if int(so_bet) > soduc:
        await update.message.reply_text("Số dư không đủ ! ",parse_mode="HTML")
        return
      check_phien_c=database.get_phien_cuoc(database.get_home_data()["phien_hien_tai"],user)
      o=database.get_home_data()
      t=o["tong_bet_tai"]
      x=o["tong_bet_xiu"]
      if bet_cua =="T":
        check_=int(t)+int(so_bet)<=int(x)+int(o["so_du_cai"])
      else:
        check_=int(x)+int(so_bet)<=int(t)+int(o["so_du_cai"])
      if check_==False:
        await update.message.reply_text(f"Cược quá hạn mức !",parse_mode="HTML")
        return
      if check_phien_c ==[]:
        soduc=int(database.get_user_data(user)[1])-int(so_bet)
        database.update_user(user,"coin",str(soduc))
        database.add_phien_cuoc(user,bet_cua,str(so_bet),database.get_home_data()['phien_hien_tai'])
      else:
        bet_cu=check_phien_c[0][1]
        coin_cu=check_phien_c[0][2]
        if bet_cu != bet_cua:
          await update.message.reply_text("Vui lòng chỉ cược 1 cửa ",parse_mode="HTML")
          return
        soduc=int(database.get_user_data(user)[1])-int(so_bet)
        database.update_user(user,"coin",str(soduc))
        allc=int(coin_cu)+int(so_bet)
        database.update_phien_cuoc(user,database.get_home_data()['phien_hien_tai'],coin=str(allc))
        
      text_b="TÀI" if bet_cua =="T" else "XỈU"
      if bet_cua =="T":
        database.update_home(tong_bet_tai=int(database.get_home_data()["tong_bet_tai"])+int(so_bet))
      else:
        database.update_home(tong_bet_xiu=int(database.get_home_data()["tong_bet_xiu"])+int(so_bet))
      if int(uid_chat) < 0:
        await update.message.reply_text(f"👤 Bạn vừa cược thành công {quy_doi(so_bet)} ₫ bên {text_b} ✅",parse_mode="HTML")
      else:
        await context.bot.send_message(
          chat_id=CHAT_ID,text=f"👤 Người chơi ẨN DANH {user[:-4]}**** vừa cược thành công {quy_doi(so_bet)} ₫ bên {text_b} ✅",parse_mode="HTML")
        await update.message.reply_text(f"👤 Bạn vừa cược thành công {quy_doi(so_bet)} ₫ bên {text_b} ✅",parse_mode="HTML")
      
      
async def sd(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  soduc=database.get_user_data(user)[1]
  await update.message.reply_text(f"Số dư của bạn là: {quy_doi(soduc)} ₫",parse_mode="HTML")




application = (Application.builder().token(token_bot).connect_timeout(60.0).read_timeout(60.0).write_timeout(60.0).pool_timeout(60.0).connection_pool_size(16).post_init(post_init).build())
application.add_error_handler(error_handler)
application.add_handler(CommandHandler("lamcai", lamcai))
application.add_handler(CommandHandler("sd", sd))

application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot Ä‘ang cháº¡y...")
application.run_polling(poll_interval=1,timeout=60,allowed_updates=Update.ALL_TYPES,)