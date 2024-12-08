import requests

# 测试登录
def test_login():
    url = 'http://127.0.0.1:5000/login'
    payload = {
        'email': 'hrqdsg@163.com',
        'password': '12345'  # 替换为您测试的密码
    }
    
    response = requests.post(url, json=payload)
    
    print("Login Response Status Code:", response.status_code)
    print("Login Response JSON:", response.json())



if __name__ == '__main__':
    test_login()          # 测试登录
