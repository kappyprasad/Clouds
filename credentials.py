import sys,re,os,console, keychain

def password(app,user):
    pwd = keychain.get_password(app,user)
    if not pwd:
        pwd = console.input_alert('%s@%s'%(user,app))
        keychain.set_password(app,user,pwd)
    return pwd

def environment(app):
    for key in [
        'AWS_REGION',
        'AWS_KEY',
        'AWS_SECRET',
    ]:
        os.environ[key] = password(app,key)
 
def main():
    for fn in os.listdir('.'):
        if fn.endswith('.py'):
            print fn
            
    return
          
if __name__ == '__main__' : main()
