from tkinter import *
from tkinter import ttk, messagebox
import psycopg2

# ---------- DB ----------
conn = psycopg2.connect(host="localhost", database="library", user="postgres", password="sql")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS students(name TEXT PRIMARY KEY, password TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS books(id SERIAL PRIMARY KEY, book_id TEXT UNIQUE, title TEXT, author TEXT, qty INT)")
cur.execute("CREATE TABLE IF NOT EXISTS issued(book_id TEXT, student TEXT)")
conn.commit()

# ---------- MAIN ----------
def open_lib(role, user=""):
    win = Tk()
    win.title(role.upper())

    book_id, title, author, qty = StringVar(), StringVar(), StringVar(), StringVar()
    student = StringVar()

    tree = ttk.Treeview(win, columns=("id","bid","title","author","qty"), show="headings")
    for c in ("id","bid","title","author","qty"): tree.heading(c, text=c)
    tree.pack(fill=BOTH, expand=True)

    def refresh():
        tree.delete(*tree.get_children())
        cur.execute("SELECT * FROM books")
        for r in cur.fetchall(): tree.insert("", END, values=r)

    def select(e):
        d = tree.item(tree.focus())["values"]
        if d:
            book_id.set(d[1]); title.set(d[2]); author.set(d[3]); qty.set(d[4])

    def add():
        cur.execute("INSERT INTO books VALUES(DEFAULT,%s,%s,%s,%s)",
                    (book_id.get(), title.get(), author.get(), int(qty.get())))
        conn.commit(); refresh()

    def update():
        cur.execute("UPDATE books SET title=%s,author=%s,qty=%s WHERE book_id=%s",
                    (title.get(), author.get(), int(qty.get()), book_id.get()))
        conn.commit(); refresh()

    def delete():
        cur.execute("DELETE FROM books WHERE book_id=%s",(book_id.get(),))
        conn.commit(); refresh()

    def issue():
        cur.execute("SELECT qty FROM books WHERE book_id=%s",(book_id.get(),))
        q = cur.fetchone()
        if q and q[0]>0:
            cur.execute("INSERT INTO issued VALUES(%s,%s)",(book_id.get(), student.get()))
            cur.execute("UPDATE books SET qty=qty-1 WHERE book_id=%s",(book_id.get(),))
            conn.commit(); refresh()
        else: messagebox.showerror("Error","Not available")

    def ret():
        cur.execute("DELETE FROM issued WHERE book_id=%s AND student=%s",(book_id.get(), user))
        cur.execute("UPDATE books SET qty=qty+1 WHERE book_id=%s",(book_id.get(),))
        conn.commit(); refresh()

    Frame(win).pack()
    for txt,var in [("ID",book_id),("Title",title),("Author",author),("Qty",qty)]:
        Label(win,text=txt).pack(); Entry(win,textvariable=var).pack()

    if role=="admin":
        Entry(win,textvariable=student).pack()
        for t,f in [("Add",add),("Update",update),("Delete",delete),("Issue",issue)]:
            Button(win,text=t,command=f).pack(fill=X)
    else:
        Button(win,text="Return",command=ret).pack(fill=X)

    tree.bind("<ButtonRelease-1>", select)
    refresh()
    win.mainloop()

# ---------- LOGIN ----------
def admin():
    if user.get()=="admin" and pwd.get()=="admin":
        root.destroy(); open_lib("admin")
    else: messagebox.showerror("Error","Wrong")

def student():
    cur.execute("SELECT password FROM students WHERE name=%s",(user.get(),))
    r = cur.fetchone()
    if r and r[0]==pwd.get():
        root.destroy(); open_lib("student", user.get())
    else: messagebox.showerror("Error","Invalid")

def signup():
    try:
        cur.execute("INSERT INTO students VALUES(%s,%s)",(user.get(), pwd.get()))
        conn.commit(); messagebox.showinfo("OK","Created")
    except: messagebox.showerror("Error","Exists")

# ---------- ROOT ----------
root = Tk()
root.title("Login")

user, pwd = StringVar(), StringVar()

Label(root,text="User").pack()
Entry(root,textvariable=user).pack()
Label(root,text="Password").pack()
Entry(root,textvariable=pwd,show="*").pack()

Button(root,text="Admin Login",command=admin).pack(fill=X)
Button(root,text="Student Login",command=student).pack(fill=X)
Button(root,text="Signup",command=signup).pack(fill=X)

root.mainloop()
