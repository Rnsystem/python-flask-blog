import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_redirect(client):
    """ルートアクセスは /top にリダイレクトされる"""
    response = client.get('/')
    assert response.status_code == 302  # リダイレクト
    assert '/top' in response.headers['Location']

def test_privacy_page(client):
    """プライバシーポリシーページが正常に表示される"""
    response = client.get('/privacy')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'プライバシー' in html or 'Privacy' in html

# def test_company_page(client):
#     """会社情報ページが正常に表示される"""
#     response = client.get('/company')
#     assert response.status_code == 200
#     html = response.get_data(as_text=True)
#     assert '会社' in html or 'Company' in html

def test_contact_get(client):
    """問い合わせページがGETで正常に表示される"""
    response = client.get('/contact')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'お問い合わせ' in html or 'Contact' in html
