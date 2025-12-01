# Hướng Dẫn Troubleshooting Publish PyPI

Tài liệu này cung cấp lời giải quyết các vấn đề phổ biến khi publish lên PyPI.

## 1. Lỗi Build Distribution

### 1.1 "No module named build"

**Lỗi:**
```
ModuleNotFoundError: No module named 'build'
```

**Nguyên Nhân:** Build module chưa được cài đặt

**Cách Sửa:**
```bash
# Cài đặt build
pip install build

# Hoặc cập nhật
pip install --upgrade build

# Test
python -m build --version
```

### 1.2 "Invalid distribution on line..."

**Lỗi:**
```
ERROR: The long_description has invalid UNKNOWN markup
```

**Nguyên Nhân:** README.md có markdown không hợp lệ

**Cách Sửa:**
```bash
# Kiểm tra README format
python -m readme_renderer README.md

# Hoặc cài đặt renderer
pip install readme_renderer

# Sửa lỗi markdown trong README.md
# Ví dụ: Không hỗ trợ HTML tags, cần dùng markdown

# Test lại
python -m build
python -m twine check dist/*
```

### 1.3 "long_description does not exist"

**Lỗi:**
```
ValueError: readme = 'README.md' does not exist
```

**Nguyên Nhân:** README.md bị xóa hoặc path sai

**Cách Sửa:**
```bash
# Kiểm tra README.md tồn tại
ls -l README.md

# Hoặc chọn file khác
ls -la *.md

# Sửa path trong pyproject.toml
# readme = "README.md"
```

### 1.4 "MANIFEST.in issues"

**Lỗi:**
```
warning: no previously-included files matching ...
```

**Nguyên Nhân:** MANIFEST.in không khớp file

**Cách Sửa:**
```bash
# Kiểm tra MANIFEST.in
cat MANIFEST.in

# Cập nhật MANIFEST.in
cat > MANIFEST.in << 'EOF'
include README.md
include LICENSE
include CHANGELOG.md
include TESTING.md
recursive-include src *.py
recursive-include tests *.py
EOF

# Rebuild
rm -rf build dist
python -m build
```

## 2. Lỗi Verification

### 2.1 "No module named twine"

**Lỗi:**
```
ModuleNotFoundError: No module named 'twine'
```

**Nguyên Nhân:** Twine chưa được cài đặt

**Cách Sửa:**
```bash
# Cài đặt twine
pip install twine

# Test
python -m twine --version
```

### 2.2 "twine check failed"

**Lỗi:**
```
Checking dist/package.whl: FAILED
```

**Nguyên Nhân:** Metadata không hợp lệ

**Cách Sửa:**
```bash
# Xem chi tiết lỗi
python -m twine check dist/* -v

# Kiểm tra README
pip install readme_renderer
python -m readme_renderer README.md

# Sửa pyproject.toml
# - Đảm bảo description ngắn gọn
# - Kiểm tra keywords format
# - Validate license field
# - Check classifiers

# Rebuild
rm -rf build dist
python -m build
python -m twine check dist/*
```

### 2.3 "Invalid classifier"

**Lỗi:**
```
Invalid classifier: 'License :: OSI Approved :: MIT'
```

**Nguyên Nhân:** Classifier không đúng định dạng

**Cách Sửa:**
```bash
# Xem danh sách valid classifiers
https://pypi.org/pypi?%3Aaction=list_classifiers

# Sửa pyproject.toml
classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: MIT License",  # Format đúng
]

# Rebuild
python -m build
```

## 3. Lỗi Authentication

### 3.1 "403 Forbidden - Invalid or expired authentication"

**Lỗi:**
```
ERROR: 403 Forbidden: Invalid or expired authentication credentials.
```

**Nguyên Nhân:** Token không hợp lệ hoặc hết hạn

**Cách Sửa:**
```bash
# 1. Tạo token mới trên PyPI
# Truy cập: https://pypi.org/account/

# 2. Copy token mới
pypi-AgEIcHlwaS5vcmc...

# 3. Cập nhật credentials
# Cách A: .pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
EOF
chmod 600 ~/.pypirc

# Cách B: Environment variables
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."

# 4. Test token
python -m twine upload --skip-existing dist/*
```

### 3.2 "401 Unauthorized"

**Lỗi:**
```
ERROR: 401 Client Error: Unauthorized
```

**Nguyên Nhân:** Credentials chưa được cấu hình

**Cách Sửa:**
```bash
# 1. Kiểm tra .pypirc tồn tại
ls -la ~/.pypirc

# 2. Hoặc set environment variables
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-..."

# 3. Test upload
python -m twine upload --skip-existing dist/*

# 4. Nếu vẫn lỗi, tạo token mới
# Xóa token cũ trên PyPI
# Tạo token mới
# Update credentials
```

### 3.3 "Invalid or nonexistent token"

**Lỗi:**
```
ERROR: Invalid or nonexistent token
```

**Nguyên Nhân:** Token bị revoke hoặc format sai

**Cách Sửa:**
```bash
# 1. Kiểm tra token format
# Phải là: pypi-... (bắt đầu với pypi-)

# 2. Kiểm tra không có spaces
# Sai: "pypi-AgEI cHlwaS5vcmc..."
# Đúng: "pypi-AgEIcHlwaS5vcmc..."

# 3. Tạo token mới
# Truy cập: https://pypi.org/account/
# Remove token cũ
# Create token mới

# 4. Cập nhật credentials
```

## 4. Lỗi Upload

### 4.1 "409 Conflict - File already exists"

**Lỗi:**
```
ERROR: 409 Conflict: File already exists. See
https://pypi.org/help/#file-name-reuse
```

**Nguyên Nhân:** Version đã được upload trước đó

**Cách Sửa - Option 1: Tăng Version**
```bash
# Sửa version trong pyproject.toml
version = "0.2.0"  # từ 0.1.0 thành 0.2.0

# Commit
git add pyproject.toml
git commit -m "chore: bump version to 0.2.0"

# Rebuild
rm -rf build dist
python -m build

# Upload lại
python -m twine upload dist/*
```

**Cách Sửa - Option 2: Yank Version Cũ**
```bash
# 1. Vào PyPI project page
# https://pypi.org/project/ennam-django-apidog/

# 2. Click "History"
# 3. Chọn version cũ (ví dụ: 0.1.0)
# 4. Click "Options" → "Yank release"

# 5. Sau đó upload lại
python -m twine upload dist/*
```

**Cách Sửa - Option 3: Re-upload (nếu lỗi tạm thời)**
```bash
# Sử dụng --skip-existing
python -m twine upload --skip-existing dist/*
```

### 4.2 "403 Forbidden - User ... is not allowed to upload"

**Lỗi:**
```
ERROR: 403 Forbidden: User is not allowed to upload
```

**Nguyên Nhân:** Token không có quyền upload cho project này

**Cách Sửa:**
```bash
# 1. Tạo token mới với scope "Entire account"
# (hoặc scope này project cụ thể)

# 2. Verify bạn là owner/maintainer của project
# - Vào PyPI project → Collaboration
# - Check role của account

# 3. Update credentials
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-..."

# 4. Test lại
python -m twine upload dist/*
```

### 4.3 "400 Bad Request"

**Lỗi:**
```
ERROR: 400 Bad Request
```

**Nguyên Nhân:** Request format sai hoặc file corrupt

**Cách Sửa:**
```bash
# 1. Verify distribution files
python -m twine check dist/*

# 2. Xóa và rebuild
rm -rf build dist
python -m build

# 3. Verify lại
python -m twine check dist/*

# 4. Upload lại
python -m twine upload dist/*
```

### 4.4 "Connection timeout"

**Lỗi:**
```
ERROR: HTTPError: [Errno 28] Connection timeout
```

**Nguyên Nhân:** Network issue hoặc PyPI server slow

**Cách Sửa:**
```bash
# 1. Chờ vài phút, thử lại
sleep 30
python -m twine upload dist/*

# 2. Kiểm tra network
ping pypi.org

# 3. Sử dụng verbose mode để xem chi tiết
python -m twine upload -v dist/*

# 4. Nếu vẫn lỗi, thử lại sau
```

## 5. Lỗi Metadata

### 5.1 "Invalid project name"

**Lỗi:**
```
ERROR: Invalid project name 'ennam django apidog'
```

**Nguyên Nhân:** Tên project không hợp lệ

**Cách Sửa:**
```bash
# Kiểm tra name trong pyproject.toml
# Phải theo quy tắc:
# - Chỉ chứa letters, numbers, hyphens, underscores
# - Bắt đầu bằng letter

# Sửa lại
name = "ennam-django-apidog"  # Đúng
# KHÔNG: name = "ennam django apidog"
```

### 5.2 "Version does not match"

**Lỗi:**
```
ERROR: Version in filename does not match version in metadata
```

**Nguyên Nhân:** Version trong pyproject.toml không khớp filename

**Cách Sửa:**
```bash
# Kiểm tra version
grep '^version' pyproject.toml
# Output: version = "0.2.0"

# Kiểm tra dist files
ls dist/
# Output: ennam_django_apidog-0.2.0*.whl

# Nếu không khớp, rebuild
rm -rf build dist
python -m build

# Verify
python -m twine check dist/*
```

### 5.3 "Author email is invalid"

**Lỗi:**
```
ERROR: Author email is invalid
```

**Nguyên Nhân:** Email format sai

**Cách Sửa:**
```bash
# Sửa authors trong pyproject.toml
authors = [
    {name = "Ennam", email = "ennam@example.com"}  # Đúng
]

# KHÔNG sử dụng format này:
# authors = ["Ennam <ennam@example.com>"]

# Rebuild
python -m build
```

## 6. Lỗi Installation

### 6.1 "Package not found" (sau upload)

**Lỗi:**
```
ERROR: Could not find a version that satisfies the requirement
ennam-django-apidog
```

**Nguyên Nhân:** PyPI chưa kip index package

**Cách Sửa:**
```bash
# 1. Chờ 5-10 phút
sleep 300

# 2. Clear pip cache
pip cache purge

# 3. Thử install lại
pip install --no-cache-dir ennam-django-apidog

# 4. Kiểm tra PyPI JSON API
curl https://pypi.org/pypi/ennam-django-apidog/json

# 5. Nếu vẫn không có, check upload logs
# Vào https://pypi.org/project/ennam-django-apidog/
```

### 6.2 "Requirement already satisfied" (TestPyPI)

**Lỗi:**
```
Requirement already satisfied: ennam-django-apidog
```

**Nguyên Nhân:** Đã cài version này từ lần trước

**Cách Sửa:**
```bash
# 1. Upgrade version
pip install --upgrade ennam-django-apidog

# 2. Hoặc force reinstall
pip install --force-reinstall ennam-django-apidog

# 3. Hoặc uninstall trước
pip uninstall ennam-django-apidog
pip install ennam-django-apidog
```

## 7. Lỗi README Rendering

### 7.1 "README rendering failed"

**Lỗi:**
```
ERROR: README rendering failed
```

**Nguyên Nhân:** README.md có markdown/reStructuredText không hợp lệ

**Cách Sửa:**
```bash
# 1. Cài readme renderer
pip install readme_renderer

# 2. Test README
python -m readme_renderer README.md

# 3. Nếu lỗi, sửa markdown:
# Không hỗ trợ: HTML tags, custom CSS
# Hỗ trợ: Standard markdown, some HTML attributes

# 4. Hoặc sử dụng .rst format
# Đổi tên README.md → README.rst
# Cập nhật pyproject.toml:
# readme = "README.rst"

# 5. Rebuild và test
python -m build
python -m twine check dist/*
```

## 8. Quick Diagnostic

Khi gặp lỗi, chạy diagnostic commands:

```bash
# 1. Check environment
python --version
python -m pip --version
python -m build --version
python -m twine --version

# 2. Check project files
ls -la pyproject.toml
ls -la README.md
ls -la CHANGELOG.md

# 3. Check distribution
rm -rf build dist
python -m build
ls -lh dist/

# 4. Validate distribution
python -m twine check dist/* -v

# 5. Check credentials
python -m twine --help | grep -i auth
# Test with:
python -m twine upload --skip-existing dist/*

# 6. Check network
ping pypi.org
curl https://pypi.org/pypi/ennam-django-apidog/json
```

## 9. Debug Mode

Chạy upload với verbose/debug output:

```bash
# Verbose mode
python -m twine upload -v dist/*

# Extra verbose
python -m twine upload -vv dist/*

# Dry run (không thực sự upload)
python -m twine upload --dry-run dist/*

# Skip existing (safe)
python -m twine upload --skip-existing dist/*
```

## 10. Kontakt Support

Nếu vẫn không giải quyết được:

1. **Check PyPI Status:** https://status.python.org/
2. **PyPI Help:** https://pypi.org/help/
3. **Twine Issues:** https://github.com/pypa/twine/issues
4. **Community:** https://discuss.python.org/

---

**Tip:** Luôn test trên TestPyPI trước khi upload production! 🚀
