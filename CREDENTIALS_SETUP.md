# Hướng Dẫn Cấu Hình PyPI Credentials

Tài liệu này hướng dẫn cách thiết lập credentials an toàn để publish lên PyPI.

## 1. Tạo API Token trên PyPI

### 1.1 Đăng Nhập PyPI

1. Truy cập: https://pypi.org/account/login/
2. Đăng nhập với tài khoản PyPI của bạn
3. Nếu chưa có tài khoản, đăng ký tại: https://pypi.org/account/register/

### 1.2 Tạo API Token

1. Sau khi đăng nhập, vào "Account settings"
2. Bên trái sidebar, click "API tokens"
3. Click nút "Create token"
4. Chọn scope:
   - "Entire account" (upload all projects)
   - Hoặc "Project specific" (chỉ cho project này)
5. Đặt tên cho token (ví dụ: "ennam-django-apidog-upload")
6. Click "Create token"

### 1.3 Copy Token

**⚠️ QUAN TRỌNG:** Token chỉ hiển thị 1 lần duy nhất!

- Copy token và lưu ở nơi an toàn
- Token sẽ có dạng: `pypi-AgEIcHlwaS5vcmc...`
- Không share token với bất kỳ ai
- Nếu quên, tạo token mới

## 2. Cấu Hình Credentials (3 Cách)

### Cách 1: Sử Dụng .pypirc (Khuyến Cáo)

Tạo hoặc chỉnh sửa file `~/.pypirc`:

**Trên Windows:**
```
C:\Users\YourUsername\.pypirc
```

**Trên macOS/Linux:**
```
~/.pypirc
```

**Nội dung file:**

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS9yd...
```

**Permissions (quan trọng):**

```bash
# macOS/Linux - chỉ owner có quyền read
chmod 600 ~/.pypirc

# Windows - không cần (NTFS đã quản lý)
```

**Sử dụng:**

```bash
# Upload lên PyPI
python -m twine upload dist/*

# Upload lên TestPyPI
python -m twine upload --repository testpypi dist/*
```

### Cách 2: Sử Dụng Environment Variables

**Trên Windows (PowerShell):**

```powershell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-AgEIcHlwaS5vcmc..."
$env:TWINE_REPOSITORY = "pypi"

# Verify
echo $env:TWINE_PASSWORD

# Publish
python -m twine upload dist/*
```

**Trên Windows (Command Prompt):**

```cmd
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...
set TWINE_REPOSITORY=pypi

python -m twine upload dist/*
```

**Trên macOS/Linux:**

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."
export TWINE_REPOSITORY="pypi"

# Verify
echo $TWINE_PASSWORD

# Publish
python -m twine upload dist/*
```

**Permanent (macOS/Linux):**

Thêm vào `~/.bashrc` hoặc `~/.zshrc`:

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."
```

Sau đó reload:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Cách 3: Command Line Arguments (Ít An Toàn)

```bash
python -m twine upload dist/ \
  --username __token__ \
  --password "pypi-AgEIcHlwaS5vcmc..."
```

**⚠️ Cảnh báo:** Method này lưu credentials trong shell history!

## 3. Credential Keyring (Nâng Cao)

Sử dụng system keyring để bảo mật tốt hơn:

### 3.1 Cài Đặt Keyring

```bash
pip install keyring
```

### 3.2 Lưu Credentials vào Keyring

**Trên Windows:**

```bash
python -m keyring set https://upload.pypi.org/legacy/ __token__
# Nhập password (token) khi được yêu cầu
```

**Trên macOS/Linux:**

```bash
python -m keyring set https://upload.pypi.org/legacy/ __token__
# Nhập password (token) khi được yêu cầu
```

### 3.3 Sử Dụng

Twine sẽ tự động lấy credentials từ keyring:

```bash
python -m twine upload dist/*
# Hoặc
python -m twine upload --repository testpypi dist/*
```

### 3.4 Kiểm Tra Credentials trong Keyring

```bash
# Xem credentials
python -m keyring get https://upload.pypi.org/legacy/ __token__

# Xóa credentials (nếu cần)
python -m keyring delete https://upload.pypi.org/legacy/ __token__
```

## 4. GitHub Secrets (Cho CI/CD)

Nếu sử dụng GitHub Actions để auto-publish:

### 4.1 Tạo Repository Secret

1. Truy cập GitHub repo settings
2. Vào "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Thêm 2 secrets:

**Secret 1: PYPI_USERNAME**
```
__token__
```

**Secret 2: PYPI_PASSWORD**
```
pypi-AgEIcHlwaS5vcmc...
```

### 4.2 Sử Dụng trong Workflow

File: `.github/workflows/publish.yml`

```yaml
- name: Publish to PyPI
  run: |
    python -m twine upload dist/*
  env:
    TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
    TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
```

## 5. TestPyPI Credentials

Tương tự như PyPI, tạo token riêng cho TestPyPI:

1. Truy cập: https://test.pypi.org/account/
2. Tạo API token
3. Thêm vào `.pypirc` hoặc environment variables

**Sử dụng TestPyPI:**

```bash
# Có .pypirc
python -m twine upload --repository testpypi dist/*

# Hoặc environment variables
export TWINE_REPOSITORY_URL="https://test.pypi.org/legacy/"
python -m twine upload dist/*
```

## 6. Best Practices (Các Thực Hành Tốt Nhất)

### 6.1 Bảo Mật Token

✅ **Nên Làm:**
- Sử dụng .pypirc với `chmod 600`
- Sử dụng environment variables
- Sử dụng system keyring
- Sử dụng GitHub Secrets cho CI/CD

❌ **Không Nên Làm:**
- Hardcode token trong code
- Commit token vào git
- Share token với người khác
- Sử dụng command line arguments (lưu trong history)

### 6.2 Quản Lý Token

```bash
# Kiểm tra PyPI tokens
# Truy cập: https://pypi.org/account/

# Rotate tokens định kỳ
# 1. Tạo token mới
# 2. Update credentials
# 3. Delete token cũ trên PyPI

# Kiểm tra token expiry
# Tokens không có expiry date, nhưng nên rotate hàng năm
```

### 6.3 Audit Trail

Lưu ý của các actions:
- Luôn dùng named tokens (ví dụ: "ennam-django-apidog-upload")
- Check PyPI project settings để xem upload history
- GitHub Actions có audit log cho tất cả actions

## 7. Troubleshooting Credentials

### Lỗi 1: "403 Forbidden - Invalid or expired authentication credentials"

```bash
# Check credentials
python -m twine --version

# Verify token valid
curl -H "Authorization: Bearer <token>" \
  https://pypi.org/pypi/ennam-django-apidog/json

# Tạo token mới nếu cần
```

### Lỗi 2: "401 Unauthorized"

```bash
# Kiểm tra .pypirc format
cat ~/.pypirc

# Hoặc test credentials
python -m twine check dist/*
```

### Lỗi 3: "No module named 'keyring'"

```bash
# Cài đặt keyring
pip install keyring

# Hoặc không dùng keyring, sử dụng .pypirc
```

### Lỗi 4: Permission Denied (.pypirc)

```bash
# macOS/Linux - sửa permissions
chmod 600 ~/.pypirc

# Kiểm tra
ls -la ~/.pypirc
# Output: -rw------- (chỉ owner có quyền)
```

## 8. Xóa Credentials (Khi Không Cần)

### 8.1 Xóa .pypirc

```bash
# Backup first
cp ~/.pypirc ~/.pypirc.backup

# Delete
rm ~/.pypirc
```

### 8.2 Xóa Environment Variables

```bash
# Trong PowerShell
Remove-Item env:TWINE_USERNAME
Remove-Item env:TWINE_PASSWORD

# Trong bash
unset TWINE_USERNAME
unset TWINE_PASSWORD
```

### 8.3 Xóa từ Keyring

```bash
python -m keyring delete https://upload.pypi.org/legacy/ __token__
```

### 8.4 Revoke Token trên PyPI

1. Truy cập: https://pypi.org/account/
2. Vào "API tokens"
3. Tìm token cần xóa
4. Click "Remove"

## 9. Testing Credentials

```bash
# Test PyPI credentials
python -m twine upload --repository testpypi --skip-existing dist/*

# Test production credentials
python -m twine upload --skip-existing dist/*

# Verbose output
python -m twine upload -v dist/*

# Dry run (không thực sự upload)
python -m twine upload --skip-existing --dry-run dist/*
```

## 10. Tài Liệu Tham Khảo

- [PyPI Help - Creating API Tokens](https://pypi.org/help/#api-tokens)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Keyring Documentation](https://github.com/jaraco/keyring)

## Quick Reference

```bash
# 1. Create .pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers = pypi testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS...
EOF

# 2. Secure .pypirc (macOS/Linux)
chmod 600 ~/.pypirc

# 3. Test credentials
python -m twine upload --repository testpypi --skip-existing dist/*

# 4. Publish to PyPI
python -m twine upload dist/*
```

---

**Remember:** Credentials là chìa khóa để publish package. Bảo vệ chúng như bảo vệ mật khẩu! 🔐
