token_bot="8117034562:AAEjDexzJdoyUO4lX6RTI-hpBqRrf0kw3j8"
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import ChatPermissions
from telegram.error import NetworkError, TimedOut, RetryAfter, BadRequest, Forbidden
import asyncio, json, requests, base64, logging, threading, re, random, httpx,sqlite3,datauser,tao_qr
from time import sleep
from telegram.ext import JobQueue
from telegram.request import HTTPXRequest
from cachetools import TTLCache

noi_dung_mgd = TTLCache(maxsize=1000, ttl=1800)

database=datauser.Database("txroom.db")
def check_rank_progress(total_money):
  if total_money < 3000000:
    return {"rank": "Đồng 🥉", "conlai": 3000000 - total_money}
  elif total_money < 9000000:
    return {"rank": "Bạc 🥈", "conlai": 9000000 - total_money}
  elif total_money < 30000000:
    return {"rank": "Vàng 🥇", "conlai": 30000000 - total_money}
  elif total_money < 60000000:
    return {"rank": "Bạc Kim ⚔️", "conlai": 60000000 - total_money}
  elif total_money < 100000000:
    return {"rank": "Lục Bảo 🐲", "conlai": 100000000 - total_money}
  elif total_money < 500000000:
    return {"rank": "Kim Cương 💎", "conlai": 500000000 - total_money}
  else:
    return {"rank": "Vua 🏆", "conlai":999999999}
def info():
  try:
    with open('info.json', 'r', encoding='utf-8') as f:
      return json.load(f)
  except FileNotFoundError:
    pass



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

async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  if user == "5907172438" and len(text)==3:
    uidnhan=text[1]
    coin=text[2]
    soduc=database.get_user_data(uidnhan)
    if soduc != None:
      sodun=int(soduc[1])+int(coin)
      database.update_user(uidnhan,"coin",str(sodun))
      await update.message.reply_text(f"Số dư mới của id: {uidnhan} là {quy_doi(sodun)} đ",parse_mode="HTML")
  
    else:
      await update.message.reply_text(f"UID KHÔNG TỒN TẠI",parse_mode="HTML")

async def muacode(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  if len(text)==3 and check_int(text[1]) and check_int(text[2]) == True:
    if int(text[1]) < 5000 or int(text[2]) <1 or int(text[2]) >10:
      await update.message.reply_text(f"Mua tối thiểu 5.000 ₫ và số lượng là 1 tối đa 10",parse_mode="HTML")
      return
    menh_gia=int(text[1])
    so_luong_nhap=int(text[2])
    tong_ban_dau=menh_gia*so_luong_nhap
    tong_tri_gia=tong_ban_dau+tinh_phan_tram(20,tong_ban_dau)
    so_du_p=int(database.get_user_data(user)[1])
    if tong_tri_gia <= so_du_p:
      so_du_n=so_du_p-tong_tri_gia
      database.update_user(user,"coin",str(so_du_n))
      text_s="Code của bạn ở đây,lưu ý mỗi code chỉ sử dụng được 1 lần,sử dụng ngay để không hết hạn\n\n"
      for i in range(so_luong_nhap):
        code_text="".join(random.choice("QWETRYUIOPLKJHGFDSAZXCVBNM0987654321") for i in range(10))
        database.add_gift_code(code_text,str(menh_gia),"1")
        text_s+=f"<code>{code_text}</code> 👈 CLICK VÀO ĐÂY ĐỂ SAO CHÉP\n"
      await update.message.reply_text(text_s,parse_mode="HTML")
    else:
      await update.message.reply_text(f"Số dư không đủ",parse_mode="HTML")
  else:
    await update.message.reply_text(f"💝 Để mua Giftcode, vui lòng thực hiện theo cú pháp sau: ( hệ thống sẽ thu phí 20% trên tổng tiền mua )\n\n<code>/muacode</code> [dấu cách] [số tiền] [dấu cách] [số lượng]\n\nVD: /muacode 10000 1\nMua Code 10K với số lượng là 1\n\nMua tối code tối thiểu 5k",parse_mode="HTML")

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  if len(text)==2:
    await update.message.reply_text("Mã giftcode đã được submit thành công, vui lòng chờ trong giây lát")
    await asyncio.sleep(random.randint(2,5))
    code_text=text[1]
    info = database.check_gift_code(code_text)
    if info:
      if int(info["so_luong"]) >=1:
        coin_n=info["coin"]
        sdung=database.use_gift_code(code_text)
        if sdung:
          so_du_user=int(database.get_user_data(user)[1])
          new_coin=so_du_user+int(coin_n)
          database.update_user(user,"coin",new_coin)
          await update.message.reply_text(f"💰️💰️💰️ Đổi giftcode thành công! Tài khoản của bạn đã được +{quy_doi(coin_n)} ₫.")
        else:
          await update.message.reply_text("Mã quà tặng không hợp lệ hoặc đã hết hạn.")
      else:
        database.delete_gift_code(code_text)
        await update.message.reply_text("Mã quà tặng không hợp lệ hoặc đã hết hạn.")
    else:
      await update.message.reply_text("Mã quà tặng không hợp lệ hoặc đã hết hạn.")
  else:
    await update.message.reply_text(f"💝 Để nhập Giftcode, vui lòng thực hiện theo cú pháp sau:\n\n/gift [dấu cách] mã giftcode\n\n➡️ Vd:   /gift CHANLEBANK_BOT",parse_mode="HTML")

async def naptien(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  text_nap="ORDER"+random.choice(["trasua","banhtrang","keongot","trada","nuocngot","chethai"])
  text_nap+="".join(random.choice("zxcvbnmlkjhgfdsapoiuytrewq1234567890") for i in range(random.randint(3,6)))
  if len(text)==2 and check_int(text[1]) and int(text[1]) >= 10000:
    qr_image = tao_qr.generate_vietqr_bytes(bank_code=info()['BANK_NAME'],bank_account=info()['STK'],amount=text[1],message=text_nap)
    caption=f"➡️ <b>Chuyển khoản theo thông tin sau:</b>\n\n🏦<b> Ngân hàng:</b> {info()['BANK_NAME']}\n💳 <b>Số tài khoản:</b> <code>{info()['STK']}</code> \n👤 <b>Chủ tài khoản:</b> {info()['CTK']}\n🔖 <b>Nội dung chuyển khoản:</b> <code>{text_nap}</code>\n💰 <b>Số tiền:</b> {quy_doi(text[1])} ₫\n\n⚠️ <b>Lưu ý:</b>\n✅ Chuyển đúng <b>SỐ TIỀN </b>và <b>NỘI DUNG</b>.\n♻️ Mỗi giao dịch có thông tin chuyển khoản RIÊNG – hãy tạo lệnh nạp mới trước mỗi lần nạp.\n🕕 Thời gian thanh toán mỗi giao dịch là 30 phút"
    noi_dung_mgd[text_nap]={"user":user,"coin":text[1]}
    await update.message.reply_photo(photo=qr_image,caption=caption,parse_mode="HTML")
  else:
    list_coin=[10000,50000,100000,200000,400000,600000,1000000,3000000,5000000,10000000,20000000,30000000]
    keyboard = []
    row = []
    for i, coin in enumerate(list_coin):
      button = InlineKeyboardButton(f"{quy_doi(coin)} ₫", callback_data=f'napbank_{coin}')
      row.append(button)
      if len(row) == 3 or i == len(list_coin) - 1:
        keyboard.append(row)
        row = []
    reply_markup=InlineKeyboardMarkup(keyboard)
    text="💳 <b>Nạp tiền qua Chuyển khoản Ngân hàng</b>\n\n➡️ Cách lấy thông tin nạp:\n\n🔸 Gõ lệnh: /napbank số tiền\nVí dụ: /napbank 100000\n🔸 Hoặc bấm nút số tiền bên dưới để lấy nhanh.\n\n⚠️ Lưu ý:\n✅ Chuyển đúng <b>SỐ TIỀN </b>và <b>NỘI DUNG</b> được cung cấp.\n✅ Mỗi lần nạp cần lấy thông tin MỚI.\n🚫 Không dùng thông tin cũ cho giao dịch sau.\n🕕 Thời gian thanh toán mỗi giao dịch là 30 phút\n💰 Nạp tối thiểu: 10.000đ"
    await update.message.reply_text(text,reply_markup=reply_markup,parse_mode="HTML")
    
async def ruttien(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  with open('code_bank.json', 'r', encoding='utf-8') as f:
    bank_id_by_code=json.load(f)
  if len(text)==4:
    stk=text[3]
    nganhang=text[2]
    sotienr=text[1]
    if bank_id_by_code.get(nganhang) and check_int(stk) and check_int(sotienr):
      if int(sotienr)<100000:
        await update.message.reply_text("Số tiền rút tối thiểu là 100.000 ₫")
        return
      soduu=database.get_user_data(user)
      if int(sotienr) > int(soduu[1]):
        await update.message.reply_text("Số dư không đủ vui lòng chơi thêm")
        return
      if int(soduu[3]) >0:
        await update.message.reply_text(f"Chưa đủ điều kiện rút tiền vui lòng chơi thêm {quy_doi(soduu[3])} ₫")
        return
      text=f"⁉️ Thông tin rút tiền về tài khoản Ngân hàng ⁉️\n\n 🏦 Ngân Hàng: {bank_id_by_code[nganhang]['name']}\n 🏧 STK : {stk}\n 💵 Số Tiền: {quy_doi(sotienr)} ₫\n\nXác nhận thông tin trên là chính xác và không khiếu nại về sau.\n\n[({nganhang}-{stk}-{sotienr})]"
      keyboard = [[InlineKeyboardButton("Hủy ❌", callback_data='xoatn')],[InlineKeyboardButton("Xác nhận ✅", callback_data='xacnhanrut')]]
      reply_markup = InlineKeyboardMarkup(keyboard)
      await update.message.reply_text(text,reply_markup=reply_markup)
    else:
      await update.message.reply_text("Sai định dạng rút tiền vui lòng xem lại hướng dẫn")
  else:
    text="🏧 Vui lòng thực hiện theo hướng dẫn sau:\n\n👉 /ruttien [dấu cách] Số tiền muốn rút [dấu cách]  Mã ngân hàng [dấu cách] Số tài khoản\n👉 VD:  Muốn rút 100k đến TK số 01234567890 tại Ngân hàng Vietcombank. Thực hiện theo cú pháp sau:\n\n/ruttien 100000 VCB 01234567890\n\n⚠️ Lưu ý: Không hỗ trợ hoàn tiền nếu bạn nhập sai thông tin Tài khoản. \n👉 Rút tối thiểu 100,000đ\n\nMÃ NGÂN HÀNG - TÊN NGÂN HÀNG\n\n"
    for i in list(bank_id_by_code.keys()):
      bank_name=bank_id_by_code[i]['name']
      text+="📌"+i+" ==> "+bank_name+"\n"
    await update.message.reply_text(text)

async def taikhoan(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text=update.effective_message.text.split()
  user = str(update.effective_user.id)
  name=str(update.effective_user.first_name)+" "+str(update.effective_user.last_name)
  so_du_data=database.get_user_data(user)
  rank=check_rank_progress(int(so_du_data[2]))
  text=f"👤 Tên tài khoản: {name}\n💳 ID Tài khoản: <code>{user}</code>\n💰 Số dư: {quy_doi(so_du_data[1])} ₫\n👑 Cấp Hạng: {rank['rank']}\n🚀 Tiến trình lên hạng: {quy_doi(rank['conlai'])} ₫"
  await update.message.reply_text(text, parse_mode="HTML")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = str(update.effective_user.id)
  check_user=database.get_user_data(user)
  if check_user == None:
    database.add_user(user,"0","0","0","0")
  keyboard = [['👤 Tài khoản', '🎲 Danh sách Game'],['💵 Nạp tiền', '💸 Rút tiền'],['🎁 Nhập GiftCode', '🛒 Mua GiftCode'],['📞Trung tâm hỗ trợ']]
  reply_markupp = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
  text="🔥<b> TÀI XỈU TELEGRAM – CHƠI LÀ PHÊ </b>🔥\n\nKhông admin nào chỉnh được kết quả, không gian lận, chỉ có may mắn thật sự!\n👉 Vào chơi ngay – công bằng tuyệt đối, minh bạch từng ván!"
  await update.message.reply_text(text,reply_markup=reply_markupp,parse_mode="HTML")
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = str(update.effective_user.id)
  text = update.message.text
  if text=="👤 Tài khoản":
    await taikhoan(update,context)
  if text=="🎁 Nhập GiftCode":
    await gift(update,context)
  if text=="🛒 Mua GiftCode":
    await muacode(update,context)
  if text=="📞Trung tâm hỗ trợ":
    keyboard = [[InlineKeyboardButton("Ấn vào để được hỗ trợ !!", url='https://t.me/Luciusgold888'),]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("<b>Trung tâm hỗ trợ trực tuyến 24/7 </b>",parse_mode="HTML",reply_markup=reply_markup)
  if text=="💵 Nạp tiền":
    await naptien(update,context)
  if text=="🎲 Danh sách Game":
    keyboard = [
      [InlineKeyboardButton("TÀI XỈU ROOM", callback_data='txroom')],
      ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("<b>Hãy chọn game mà muốn chơi 👇👇👇</b>",parse_mode="HTML",reply_markup=reply_markup)
  if text=="💸 Rút tiền":
    await ruttien(update,context)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  user=str(query.from_user.id)
  text=query.message.text
  if "dongy_" in query.data:
    userr=str(query.data).split('_')[1]
    sotienh=str(query.data).split('_')[2]
    await context.bot.send_message(chat_id=int(userr),text="✅ Đã rút tiền về thành công !!!")
    new_text=query.message.caption+"\n✅ Đã duyệt thành công "
    await query.message.edit_caption(caption=new_text,parse_mode="HTML",reply_markup=None)
  if "tuchoi_" in query.data:
    userr=str(query.data).split('_')[1]
    sotienh=str(query.data).split('_')[2]
    sotienu=database.get_user_data(userr)[1]
    sotienm=int(sotienu)+int(sotienh)
    database.update_user(userr,"coin",sotienm)
    await context.bot.send_message(chat_id=int(userr),text="Đơn rút tiền của bạn bị từ chối vui lòng inbox cskh để biết thêm chi tiết")
    new_text=query.message.caption+"\n❌ Đã từ chối"
    await query.message.edit_caption(caption=new_text,parse_mode="HTML",reply_markup=None)
  if query.data=="xoatn":
    await query.message.delete()
  if query.data=="xacnhanrut":
    datar=text.split("[(")[1].split(')]')[0]
    nganhang,stk,sotienr=datar.split('-')
    soduu=database.get_user_data(user)
    if int(sotienr) > int(soduu[1]):
      await query.message.reply_text("Số dư không đủ vui lòng chơi thêm")
      return
    if int(soduu[3]) >0:
      await query.message.reply_text(f"Chưa đủ điều kiện rút tiền vui lòng chơi thêm {quy_doi(soduu[3])} ₫")
      return
    sodumoi=int(soduu[1])-int(sotienr)
    database.update_user(user,"coin",str(sodumoi))
    database.update_user(user,"tong_nap","0")
    await query.message.reply_text("✅ Yêu cầu rút tiền đã được thực hiện. Vui lòng chờ trong giây lát.")
    await query.message.edit_reply_markup(reply_markup=None)
    nd=random.choice(["hoanhang","trahang","tiktok","tiki","live","taxi"])+"".join(random.choice("qwertyuioplkjhgfdsazxcvbnm0987654321") for i in range(4))
    qr_image = tao_qr.generate_vietqr_bytes(bank_code=nganhang,bank_account=stk,amount=sotienr,message=nd)
    keyboard = [[InlineKeyboardButton("Hủy ❌", callback_data=f'tuchoi_{user}_{sotienr}')],[InlineKeyboardButton("Xác nhận ✅", callback_data=f'dongy_{user}_{sotienr}')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text=f"YÊU CẦU RÚT TIỀN !!!\nPLAYER: [<a href='tg://user?id={user}'>Player</a>]\nNGÂN HÀNG: {nganhang}\nSTK: <code>{stk}</code>\nSỐ TIỀN: {quy_doi(sotienr)} ₫\nNỘI DUNG: {nd}\nUID: {user}"
    await context.bot.send_photo(chat_id=-1003056110086,photo=qr_image,caption=text,parse_mode="HTML",reply_markup=reply_markup)
  if "napbank_" in query.data:
    text_nap="ORDER"+random.choice(["trasua","banhtrang","keongot","trada","nuocngot","chethai"])
    text_nap+="".join(random.choice("zxcvbnmlkjhgfdsapoiuytrewq1234567890") for i in range(random.randint(3,6)))
    text=str(query.data).split("napbank_")
    qr_image = tao_qr.generate_vietqr_bytes(bank_code=info()['BANK_NAME'],bank_account=info()['STK'],amount=text[1],message=text_nap)
    caption=f"➡️ <b>Chuyển khoản theo thông tin sau:</b>\n\n🏦<b> Ngân hàng:</b> {info()['BANK_NAME']}\n💳 <b>Số tài khoản:</b> <code>{info()['STK']}</code> \n👤 <b>Chủ tài khoản:</b> {info()['CTK']}\n🔖 <b>Nội dung chuyển khoản:</b> <code>{text_nap}</code>\n💰 <b>Số tiền:</b> {quy_doi(text[1])} ₫\n\n⚠️ <b>Lưu ý:</b>\n✅ Chuyển đúng <b>SỐ TIỀN </b>và <b>NỘI DUNG</b>.\n♻️ Mỗi giao dịch có thông tin chuyển khoản RIÊNG – hãy tạo lệnh nạp mới trước mỗi lần nạp.\n🕕 Thời gian thanh toán mỗi giao dịch là 30 phút"
    noi_dung_mgd[text_nap]={"user":user,"coin":text[1]}
    await query.message.reply_photo(photo=qr_image,caption=caption,parse_mode="HTML")
  if query.data=="txroom":
    text="🎲<b> Tài xỉu tự làm cái </b>🎲\n\n 🎮 Tham gia group để chơi: https://t.me/tubaoduongtxroom\n\n 🎮 Cách chơi:\n\nMỗi phiên Tài Xỉu kéo dài 118 giây.\n👉 Làm CÁI (19 giây):\n\n➡️ /lamcai: Lựa chọn làm CÁI với lệch cửa 1M.\n➡️ /lamcai (số tiền lệch cửa): Lựa chọn làm CÁI với lệch cửa tuỳ ý. (Tối thiểu 1M)\n➡️ /lamcai allin: Lựa chọn làm CÁI bằng toàn bộ số dư đang có. (Tối thiểu 1M)\n\n👉 ĐẶT CƯỢC (99 giây):\n➡️ Đặt cửa TÀI: T (số tiền)\n➡️ Đặt cửa XỈU: X (số tiền)\n\n👉 KẾT QUẢ:\n➡️ Hệ thống sẽ tung 3 viên xúc xắc.\n➡️ Tài: Tổng điểm từ 11 đến 18\n➡️ Xỉu: Tổng điểm từ 3 đến 10\n\n⚠️ Lưu ý: Trong thời gian làm CÁI, hệ thống tạm hold một khoản tiền tương ứng tiền lệch cửa của CÁI."
    keyboard = [[InlineKeyboardButton("Chơi ngay !!!", url='https://t.me/tubaoduongtxroom'),]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(text,reply_markup=reply_markup,parse_mode="HTML")
    
async def background_task(application: Application):
  while True:
    try:
      await asyncio.sleep(20)
      url = f"https://api.sieuthicode.net/historyapivcb/65e7e7f579d0c04c3958029bc083f04d"
      res = requests.get(url, timeout=10)
      data=res.json()
      if data.get("code") != "00":
        await application.bot.send_message(chat_id=5907172438,text="Xay ra loi VCB")
        print("Xảy ra lỗi khi lấy lịch sử VCB")
        continue
    except:
      await application.bot.send_message(chat_id=5907172438,text="Xay ra loi VCB")
      print("Xảy ra lỗi khi đăng nhập VCB")
      continue
    print("Đăng nhập thành công VCB !!!")
    for x in data['transactions']:
      mgd=x.get("Reference", "")
      sotien=x.get("Amount", "0").replace(",", "").replace(".", "")
      noidung=x.get("Description", "")
      if database.get_nap_tien(mgd)==None:
        taxi_match = re.search(r'\bORDER[A-Za-z0-9]+\b', noidung)
        if taxi_match:
          taxi_code = taxi_match.group(0)
          data=noi_dung_mgd.get(taxi_code)
          if data:
            lenh_sotien=int(noi_dung_mgd[taxi_code]['coin'])
            lenh_uid=noi_dung_mgd[taxi_code]['user']
            if int(sotien) == lenh_sotien:
              if database.get_user_data(str(lenh_uid)) != None:
                sodun=database.get_user_data(str(lenh_uid))
                so_tien_new=int(sodun[1])+lenh_sotien
                database.update_user(str(lenh_uid),"coin",str(so_tien_new))
                t_t_nap=int(sodun[3])+round(lenh_sotien*2)
                database.update_user(str(lenh_uid),"tong_nap",str(t_t_nap))
                text=f"✅ Nạp tiền thành công !!!!\n➡️ Nội dung: {taxi_code}\n➡️ Số tiền: {quy_doi(lenh_sotien)} ₫\n➡️ Số dư hiện tại: {quy_doi(so_tien_new)} ₫"
                noi_dung_mgd.pop(taxi_code,None)
                database.add_nap_tien(mgd,str(sotien),lenh_uid)
                
                await application.bot.send_message(chat_id=int(lenh_uid),text=text,parse_mode="HTML")
                
async def post_init(application: Application):
  await application.bot.send_message(chat_id=5907172438, text="🤖 Bot đã khởi động thành công!")
  asyncio.create_task(background_task(application))
application = (Application.builder().token(token_bot).connect_timeout(60.0).read_timeout(60.0).write_timeout(60.0).pool_timeout(60.0).connection_pool_size(16).post_init(post_init).build())
application.add_error_handler(error_handler)
application.add_handler(CommandHandler("addcoin", addcoin))
application.add_handler(CommandHandler("napbank", naptien))
application.add_handler(CommandHandler("taikhoan", taikhoan))
application.add_handler(CommandHandler("muacode", muacode))
application.add_handler(CommandHandler("ruttien", ruttien))
application.add_handler(CommandHandler("gift", gift))
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_callback))
application.run_polling(poll_interval=1,timeout=60,allowed_updates=Update.ALL_TYPES,)



list_nap={"TAXI24rxn9":{"user":"123","coin":234},"TAXI71B":{"user":"000","coin":234}
  
}
text="MBVCB.11518958197.914646 TAXI24rxn9 CT tu 0371000462958 PHAN QUANG HUY HOANG toi 8886191201 TRAN THI CHUC MAI tai BIDV30/10/2025	5419 - 86794	Chuyển đi	200,00"