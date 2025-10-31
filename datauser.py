import sqlite3,random

class Database:
  def __init__(self,name):
    self.dt=name
    self.initialize_database()
  def initialize_database(self):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS home (
        phien_hien_tai TEXT,
        so_du_cai TEXT,
        cai TEXT,
        hu_coin TEXT,
        tong_bet_xiu TEXT,
        tong_bet_tai TEXT,
        trang_thai TEXT)
    ''')
    cursor.execute('SELECT COUNT(*) FROM home')
    count = cursor.fetchone()[0]
    if count == 0:
      cursor.execute('''
      INSERT INTO home (phien_hien_tai, so_du_cai, cai, hu_coin,tong_bet_xiu,tong_bet_tai, trang_thai)
            VALUES (?, ?, ?, ?,?,?, ?)''', ('0', '0', '0','0','0' ,'0', 'active'))
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS gift_code (
        code TEXT,
        coin TEXT,
        so_luong TEXT)
    ''')
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS nap_tien (
        mgd TEXT,
        sotien TEXT,
        uid TEXT)
    ''')
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS phien_cuoc (
        uid TEXT,
        bet TEXT,
        coin TEXT,
        phien_cuoc TEXT)
    ''')
    
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS phien_cai (
        uid TEXT,
        coin TEXT,
        phien_cuoc TEXT)
    ''')
    
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS lich_su_phien (
        tong_bet_xiu TEXT,
        tong_bet_tai TEXT,
        bet_win TEXT,
        phien_cuoc TEXT)
    ''')
    
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS coin_user (
        uid TEXT,
        coin TEXT,
        rank TEXT,
        tong_nap TEXT,
        tong_cuoc TEXT)
    ''')
    
    
    conn.commit()
    conn.close()
  def get_phien_cuoc(self, phien_cuoc=None, uid=None, search=None):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    if search:
      cursor.execute('SELECT * FROM phien_cuoc WHERE phien_cuoc LIKE ?', (f'%{search}%',))
    elif phien_cuoc and uid:
      cursor.execute('SELECT * FROM phien_cuoc WHERE phien_cuoc = ? AND uid = ?', (phien_cuoc, uid))
    elif phien_cuoc:
      cursor.execute('SELECT * FROM phien_cuoc WHERE phien_cuoc = ?', (phien_cuoc,))
    elif uid:
      cursor.execute('SELECT * FROM phien_cuoc WHERE uid = ?', (uid,))
    else:
      cursor.execute('SELECT * FROM phien_cuoc')
    data = cursor.fetchall()
    conn.close()
    return data
  def get_phien_cai(self, phien_cuoc=None, uid=None, search=None):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    if search:
      cursor.execute('SELECT * FROM phien_cai WHERE phien_cuoc LIKE ?', (f'%{search}%',))
    elif phien_cuoc and uid:
      cursor.execute('SELECT * FROM phien_cai WHERE phien_cuoc = ? AND uid = ?', (phien_cuoc, uid))
    elif phien_cuoc:
      cursor.execute('SELECT * FROM phien_cai WHERE phien_cuoc = ?', (phien_cuoc,))
    elif uid:
      cursor.execute('SELECT * FROM phien_cai WHERE uid = ?', (uid,))
    else:
      cursor.execute('SELECT * FROM phien_cai')
    data = cursor.fetchall()
    conn.close()
    return data
  def add_phien_cuoc(self, uid, bet, coin, phien_cuoc):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO phien_cuoc (uid, bet, coin, phien_cuoc)
        VALUES (?, ?, ?, ?)
    ''', (uid, bet, coin, phien_cuoc))
    conn.commit()
    conn.close()
  def add_phien_cai(self, uid, coin, phien_cuoc):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO phien_cai (uid, coin, phien_cuoc)
        VALUES (?, ?, ?)
    ''', (uid, coin, phien_cuoc))
    conn.commit()
    conn.close()
  def get_home_data(self):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('SELECT phien_hien_tai, so_du_cai, cai, hu_coin,tong_bet_xiu,tong_bet_tai, trang_thai FROM home LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    if row:
      return {'phien_hien_tai': row[0],'so_du_cai': row[1],'cai': row[2],'hu_coin': row[3],'tong_bet_xiu':row[4],'tong_bet_tai':row[5],'trang_thai': row[6]}
    return None
  def update_home(self, phien_hien_tai=None, so_du_cai=None, cai=None, hu_coin=None, tong_bet_xiu=None,tong_bet_tai=None,trang_thai=None):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('SELECT rowid FROM home LIMIT 1')
    row = cursor.fetchone()
    if row:
      updates = []
      values = []
      if tong_bet_xiu is not None:
        updates.append('tong_bet_xiu = ?')
        values.append(tong_bet_xiu)
      if tong_bet_tai is not None:
        updates.append('tong_bet_tai = ?')
        values.append(tong_bet_tai)
      if phien_hien_tai is not None:
        updates.append('phien_hien_tai = ?')
        values.append(phien_hien_tai)
      if so_du_cai is not None:
        updates.append('so_du_cai = ?')
        values.append(so_du_cai)
      if cai is not None:
        updates.append('cai = ?')
        values.append(cai)
      if hu_coin is not None:
        updates.append('hu_coin = ?')
        values.append(hu_coin)
      if trang_thai is not None:
        updates.append('trang_thai = ?')
        values.append(trang_thai)
      if updates:
        values.append(row[0])
        query = f"UPDATE home SET {', '.join(updates)} WHERE rowid = ?"
        cursor.execute(query, values)
    conn.commit()
    conn.close()
  def get_user_data(self,username):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
          SELECT * FROM coin_user WHERE uid = ?
      ''', (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
  def get_nap_tien(self,username):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
          SELECT * FROM nap_tien WHERE mgd = ?
      ''', (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
  def update_user(self,username,target,data):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute(f'''
          UPDATE coin_user SET {target} = ? WHERE uid = ?
      ''', (data, username))
    conn.commit()
    conn.close()
  def add_user(self,username, coin,rank ,tong_nap, tong_cuoc):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    try:
      cursor.execute('''
      INSERT INTO coin_user (uid, coin,rank ,tong_nap, tong_cuoc)VALUES (?, ?, ?,?, ?)
          ''', (username, coin, rank,tong_nap, tong_cuoc))
          
      conn.commit()
      return True
    except sqlite3.IntegrityError:
      return False
      
    finally:
      conn.close()
  def add_nap_tien(self,mgd, sotien,uid):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    try:
      cursor.execute('''
      INSERT INTO nap_tien (mgd, sotien,uid )VALUES (?, ?, ?)
          ''', (mgd, sotien, uid))
          
      conn.commit()
      return True
    except sqlite3.IntegrityError:
      return False
      
    finally:
      conn.close()
  def get_lich_su_phien(self, limit=12):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM lich_su_phien 
        ORDER BY rowid DESC 
        LIMIT ?
    ''', (limit,))
    data = cursor.fetchall()
    conn.close()
    return data[::-1]
  def add_lich_su_phien(self, tong_bet_xiu, tong_bet_tai, bet_win, phien_cuoc):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO lich_su_phien (tong_bet_xiu, tong_bet_tai, bet_win, phien_cuoc)
        VALUES (?, ?, ?, ?)
    ''', (tong_bet_xiu, tong_bet_tai, bet_win, phien_cuoc))
    conn.commit()
    conn.close()
  def update_phien_cuoc(self, uid, phien_cuoc, bet=None, coin=None):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    updates = []
    values = []
    if bet is not None:
        updates.append('bet = ?')
        values.append(bet)
    if coin is not None:
        updates.append('coin = ?')
        values.append(coin)
    if updates:
        values.extend([uid, phien_cuoc])
        query = f"UPDATE phien_cuoc SET {', '.join(updates)} WHERE uid = ? AND phien_cuoc = ?"
        cursor.execute(query, values)
    
    conn.commit()
    conn.close()
  def add_gift_code(self, code, coin, so_luong):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    try:
      cursor.execute('INSERT INTO gift_code (code, coin, so_luong) VALUES (?, ?, ?)', (code, coin, so_luong))
      conn.commit()
      return True
    except:
      return False
    finally:
      conn.close()
  def check_gift_code(self, code):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('SELECT coin, so_luong FROM gift_code WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    if result:
      return {'coin': result[0], 'so_luong': result[1]}
    return None

  def use_gift_code(self, code):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('SELECT coin FROM gift_code WHERE code = ? AND CAST(so_luong AS INTEGER) > 0', (code,))
    result = cursor.fetchone()
    if result is None:
      conn.close()
      return None
    coin = result[0]
    cursor.execute('UPDATE gift_code SET so_luong = so_luong - 1 WHERE code = ? AND CAST(so_luong AS INTEGER) > 0', (code,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return coin if success else None
  
  def clear_gift_code(self):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gift_code')
    conn.commit()
    conn.close()
    return True
  
  def delete_gift_code(self, code):
    conn = sqlite3.connect(self.dt)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gift_code WHERE code = ?', (code,))
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success
a=Database("txroom.db")
#a.clear_gift_code()
#b=a.add_phien_cuoc("123","T","1000000","8")
# a.update_user("8438122215","coin", "5000000")
# a.update_user("5049676925","coin", "5000000")
# a.update_user("5907172438","coin", "5000000")

#print(b)
# for i in range(10):
#     a.add_phien_cuoc(str(i),"X","10000011","8")
#b=a.get_lich_su_phien()
#print(b)
##a.update_home(tong_bet_tai="1000000")

#a.add_user("83861412","10000000000000000000000000000000000000","0","0","0") 
#a.add_user("8448135713","10000000","0","0","0") 
# a.add_user("5049676925","5000000","0","0","0") 
# a.add_user("5907172438","5000000","0","0","0") 











  


