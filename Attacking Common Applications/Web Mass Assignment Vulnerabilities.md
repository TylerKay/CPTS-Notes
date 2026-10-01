> ⚠️ Reviewing source code (when provided, e.g., white-box tests) makes mass assignment trivial to spot — always grep for how form/JSON params get bound directly to model objects or DB inserts.

---

## 1. What Is Mass Assignment?

- Many frameworks offer **mass assignment**: taking a full set of user-submitted form/JSON fields and binding them directly to an object or DB row in one step, reducing boilerplate.
- **The vulnerability:** if there's no whitelist restricting which fields can be set this way, an attacker can add **extra parameters** to the request and have them applied to fields they were never meant to control (e.g., `admin`, `role`, `confirmed`, `balance`).
- Attackers typically discover the hidden/unprotected fields by **reversing the client/source code** (or guessing based on common patterns) and then injecting matching parameter names into the request.

---

## 2. Classic Example — Ruby on Rails

### Intended Model

```ruby
class User < ActiveRecord::Base
  attr_accessible :username, :email
end
```

Only `username` and `email` are _meant_ to be settable.

### Attack
Attacker adds an unlisted field to the submitted params:

```json
{ "user": { "username": "hacker", "email": "hacker@example.com", "admin": true } }
```

If the framework/version in use doesn't strictly enforce the `attr_accessible` whitelist at the point of assignment, `admin: true` gets applied anyway → **instant privilege escalation** via a normal POST request.

---

## 3. Case Study — Asset Manager Web App

### Step 1 — Normal Registration Flow

Register a user → get `Success!!` → log in → blocked with:

```
Account is pending for approval
```

### Step 2 — Review Server-Side Code (`app.py`)

**Login check:**

```python
for i,j,k in cur.execute('select * from users where username=? and password=?',(username,password)):
  if k:
    session['user']=i
    return redirect("/home",code=302)
  else:
    return render_template('login.html',value='Account is pending for approval')
```

- `k` = the third column in the `users` table (the "confirmed"/approved flag).
- Login only proceeds to `/home` if that flag is **truthy**.

**Registration logic:**

```python
try:
  if request.form['confirmed']:
    cond=True
except:
  cond=False
with sqlite3.connect("database.db") as con:
  cur = con.cursor()
  cur.execute('select * from users where username=?',(username,))
  if cur.fetchone():
    return render_template('index.html',value='User exists!!')
  else:
    cur.execute('insert into users values(?,?,?)',(username,password,cond))
    con.commit()
    return render_template('index.html',value='Success!!')
```

**The flaw:** the app reads a `confirmed` field straight from the submitted form. If it's present at all (any truthy value), `cond` is set to `True` and stored directly as the approval flag — no server-side authorization check, no admin approval step actually enforced.

### Step 3 — Exploit via Burp Suite

Intercept the `/register` POST request and manually add the `confirmed` parameter:

```
username=new&password=test&confirmed=test
```

The mere **presence** of `confirmed` (regardless of value) causes `cond = True`.

### Step 4 — Log In Immediately

Log in with `new:test` → **successful login, no approval wait** — mass assignment fully bypasses the intended admin-approval workflow.

---

## 4. Prevention

**Core principle:** Explicitly whitelist assignable attributes — never trust that "the field wasn't in the form on the frontend" means it can't be sent in the raw request.

### Rails Example — Strong Parameters

```ruby
class UsersController < ApplicationController
  def create
    @user = User.new(user_params)
    if @user.save
      redirect_to @user
    else
      render 'new'
    end
  end

  private

  def user_params
    params.require(:user).permit(:username, :email)
  end
end
```

`user_params` returns **only** `username` and `email` — any extra fields (like `admin`) sent by an attacker are silently dropped before ever reaching the model.

### General Guidance (Any Stack)

- Never bind raw request bodies directly to models/DB rows.
- Maintain an explicit **allowlist** of fields permitted per endpoint/action.
- Enforce sensitive state changes (approval, roles, admin flags) via **separate, authenticated, server-controlled logic** — never let them be settable via user-supplied request parameters at all.
- Review every "convenience" feature (ORM auto-binding, form-to-object mapping) for hidden overreach.

---

## Summary

| Step                  | What Happened                                                                 |
| --------------------- | ----------------------------------------------------------------------------- |
| Framework convenience | Auto-binds all submitted params to model/DB fields                            |
| Missing whitelist     | No restriction on which fields can be set                                     |
| Attacker technique    | Add extra parameter (e.g., `admin=true`, `confirmed=1`) not present in the UI |
| Impact                | Privilege escalation, bypassed approval workflows, data tampering             |
| Fix                   | Explicit allowlisting (e.g., Rails Strong Parameters / `permit`)              |

## Key Takeaways

- Mass assignment bugs are found by looking for **any field the UI hides but the backend still accepts** — test by adding extra params to captured requests (Burp Repeater is ideal for this).
- Source-code review massively accelerates finding these — search for raw dictionary/param unpacking into models or SQL inserts (`request.form[...]`, `attr_accessible`, `Model.new(params)`, etc.).
- The presence check bug pattern (`if request.form['field']:`) is especially dangerous — an attacker doesn't even need to send a _meaningful_ value, just the field's presence can flip a boolean flag.
- Fix is always the same: **explicit allowlists**, never implicit trust of full request payloads.