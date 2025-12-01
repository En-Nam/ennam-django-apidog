# Hướng Dẫn Publish Thủ Công lên PyPI

Tài liệu này hướng dẫn cách publish thư viện `ennam-django-apidog` lên PyPI một cách thủ công.

## Yêu Cầu Tiên Quyết

### 1. Tài Khoản PyPI

Tạo tài khoản trên PyPI (nếu chưa có):
- Đăng ký tại: https://pypi.org/account/register/
- Hoặc sử dụng TestPyPI để test trước: https://test.pypi.org/account/register/

### 2. Cài Đặt Công Cụ Cần Thiết

```bash
# Cài đặt build tools
pip install build twine

# Hoặc cập nhật nếu đã có
pip install --upgrade build twine
```

### 3. Kiểm Tra Các Yêu Cầu Trước Khi Publish

```bash
# Chạy tất cả các test
pytest --cov=src --cov-report=html

# Kiểm tra type safety
mypy src/ --strict

# Kiểm tra linting
ruff check src/ tests/

# Chạy pre-commit hooks
pre-commit run --all-files
```

Tất cả các bước trên phải PASS trước khi tiếp tục.

## Bước 1: Chuẩn Bị Release

### 1.1 Cập Nhật Version

Mở file `pyproject.toml` và cập nhật version:

```toml
[project]
version = "0.2.0"  # Thay đổi từ 0.1.0
```

### 1.2 Cập Nhật CHANGELOG

Mở file `CHANGELOG.md` và thêm release notes:

```markdown
## [0.2.0] - 2024-12-01

### Added
- Thêm tính năng A
- Thêm tính năng B

### Fixed
- Sửa lỗi X
- Sửa lỗi Y

### Changed
- Thay đổi API Z
```

### 1.3 Commit Changes

```bash
# Staged tất cả các thay đổi
git add pyproject.toml CHANGELOG.md

# Commit với message rõ ràng
git commit -m "chore: prepare release v0.2.0"

# Kiểm tra commit
git log -1
```

## Bước 2: Tạo Git Tag

```bash
# Tạo annotated tag (khuyến cáo)
git tag -a v0.2.0 -m "Release version 0.2.0"

# Hoặc lightweight tag
git tag v0.2.0

# Xem tag vừa tạo
git tag -l v0.2.0 -n1
```

## Bước 3: Push Tag lên Repository

```bash
# Push tag đơn
git push origin v0.2.0

# Hoặc push tất cả tags
git push origin --tags

# Kiểm tra tag trên GitHub
# Truy cập: https://github.com/ennam/ennam-django-apidog/releases
```

## Bước 4: Build Distribution

### 4.1 Xóa Build Cũ (Nếu Có)

```bash
# Windows
rmdir /s /q build dist *.egg-info

# macOS/Linux
rm -rf build dist *.egg-info
```

### 4.2 Build Wheel và Source Distribution

```bash
# Build cả wheel và sdist
python -m build

# Kiểm tra các file vừa tạo
ls -lh dist/
```

Output sẽ giống:
```
ennam_django_apidog-0.2.0-py3-none-any.whl      (wheel)
ennam_django_apidog-0.2.0.tar.gz                 (source distribution)
```

### 4.3 Verify Distribution Files

```bash
# Kiểm tra metadata của distributions
python -m twine check dist/*

# Output phải là:
# Checking dist/ennam_django_apidog-0.2.0-py3-none-any.whl: PASSED
# Checking dist/ennam_django_apidog-0.2.0.tar.gz: PASSED
```

## Bước 5: Test Trước Khi Publish (Optional nhưng Khuyến Cáo)

### 5.1 Publish lên TestPyPI Trước

TestPyPI là PyPI sandbox để test trước khi publish production:

```bash
# Publish lên TestPyPI
python -m twine upload --repository testpypi dist/*

# Nhập username và password khi được yêu cầu
# Username: __token__
# Password: <your-testpypi-token>
```

### 5.2 Test Cài Đặt từ TestPyPI

```bash
# Tạo virtual environment test
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Cài đặt từ TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  ennam-django-apidog

# Test import
python -c "import ennam_django_apidog; print('Success!')"

# Test version
python -c "from ennam_django_apidog import __version__; print(__version__)"

# Deactivate virtual environment
deactivate

# Xóa test environment
rm -rf test_env
```

Nếu test thành công, có thể tiếp tục với production PyPI.

## Bước 6: Publish lên PyPI Production

### 6.1 Chuẩn Bị API Token

Có 2 cách để authenticate:

**Cách 1: Sử dụng API Token (Khuyến Cáo)**

1. Truy cập PyPI: https://pypi.org/account/
2. Đăng nhập vào tài khoản
3. Vào "Account settings" → "API tokens"
4. Tạo token mới với scope "Entire account"
5. Copy token (chỉ hiển thị 1 lần)

**Cách 2: Sử dụng Username/Password**

Sử dụng trực tiếp username và password PyPI (ít an toàn hơn).

### 6.2 Cấu Hình Credentials (Tùy Chọn)

Tạo/cập nhật file `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...  # Paste token ở đây

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5v...  # Paste TestPyPI token
```

### 6.3 Upload lên PyPI

```bash
# Nếu đã cấu hình .pypirc
python -m twine upload dist/*

# Hoặc upload trực tiếp với token (không cần .pypirc)
python -m twine upload dist/* --username __token__ --password "pypi-AgEIcHlwaS5vcmc..."

# Hoặc sử dụng environment variable
export TWINE_USERNAME=__token__
export TWINE_PASSWORD="pypi-AgEIcHlwaS5vcmc..."
python -m twine upload dist/*
```

**Output khi thành công:**

```
Uploading ennam_django_apidog-0.2.0-py3-none-any.whl
100%|████████| 19kB/19kB [00:02<00:00, 8.47kB/s]
Uploading ennam_django_apidog-0.2.0.tar.gz
100%|████████| 25kB/25kB [00:01<00:00, 24.3kB/s]

View at:
https://pypi.org/project/ennam-django-apidog/0.2.0/
```

## Bước 7: Xác Minh Package trên PyPI

### 7.1 Chờ PyPI Index

```bash
# Đợi 5-10 phút để PyPI index package
# Trong lúc chờ, package có thể chưa hiện trên web
```

### 7.2 Kiểm Tra Package Page

```bash
# Truy cập trên browser
https://pypi.org/project/ennam-django-apidog/

# Hoặc kiểm tra bằng command
curl https://pypi.org/pypi/ennam-django-apidog/json | python -m json.tool
```

### 7.3 Test Cài Đặt từ PyPI

```bash
# Tạo virtual environment mới
python -m venv final_test
source final_test/bin/activate  # Windows: final_test\Scripts\activate

# Cài đặt từ PyPI production
pip install ennam-django-apidog

# Test import
python -c "import ennam_django_apidog; print('Installation successful!')"

# Kiểm tra version
pip show ennam-django-apidog

# Cleanup
deactivate
rm -rf final_test
```

## Bước 8: Tạo GitHub Release (Optional)

Tạo release trên GitHub để có bản backup và changelog:

```bash
# Nếu chưa push tag
git push origin v0.2.0

# Hoặc push tất cả
git push origin --tags
```

Sau đó:
1. Truy cập: https://github.com/ennam/ennam-django-apidog/releases
2. Click "Draft a new release"
3. Chọn tag vừa tạo (v0.2.0)
4. Thêm release notes từ CHANGELOG.md
5. Publish release

## Troubleshooting

### Lỗi 1: "Invalid distribution on line..."

**Nguyên Nhân:** Metadata không hợp lệ

**Cách Sửa:**
```bash
# Check lại metadata
python -m twine check dist/*

# Sửa lỗi trong pyproject.toml hoặc README.md
# Rebuild distribution
rm -rf dist/
python -m build
python -m twine check dist/*
```

### Lỗi 2: "403 Forbidden - Invalid or expired authentication credentials"

**Nguyên Nhân:** Token không hợp lệ hoặc hết hạn

**Cách Sửa:**
```bash
# Tạo token mới trên PyPI
# https://pypi.org/account/

# Test token
python -m twine upload --repository testpypi --skip-existing dist/*

# Nếu success, upload production
python -m twine upload dist/*
```

### Lỗi 3: "409 Conflict - File already exists"

**Nguyên Nhân:** Version đã được publish trước đó

**Cách Sửa:**
1. Không thể re-publish cùng version
2. Phải bump version mới
3. Hoặc yank (ẩn) version cũ trên PyPI

```bash
# Yank version cũ (trên PyPI web):
# 1. Vào project page
# 2. Click "History"
# 3. Chọn version cần yank
# 4. Click "Yank release"
```

### Lỗi 4: "Package not found on PyPI" (sau khi upload)

**Nguyên Nhân:** PyPI chưa kip index package

**Cách Sửa:**
```bash
# Chờ 5-10 phút
# Clear pip cache
pip cache purge

# Thử install lại
pip install --no-cache-dir ennam-django-apidog
```

### Lỗi 5: "README rendering failed"

**Nguyên Nhân:** README.md có syntax markdown không hợp lệ

**Cách Sửa:**
```bash
# Validate README
python -m twine check dist/*

# Hoặc kiểm tra local
pip install readme-renderer
python -m readme_renderer README.md
```

## Quick Checklist

```bash
# ✓ Chạy tất cả tests
pytest --cov=src --cov-report=html

# ✓ Type checking
mypy src/ --strict

# ✓ Linting
ruff check src/ tests/

# ✓ Update version
# Edit pyproject.toml version = "0.2.0"

# ✓ Update CHANGELOG
# Edit CHANGELOG.md with release notes

# ✓ Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v0.2.0"

# ✓ Create git tag
git tag -a v0.2.0 -m "Release version 0.2.0"

# ✓ Push tag
git push origin v0.2.0

# ✓ Clean build
rm -rf build dist *.egg-info

# ✓ Build distributions
python -m build

# ✓ Verify distributions
python -m twine check dist/*

# ✓ (Optional) Test on TestPyPI
python -m twine upload --repository testpypi dist/*

# ✓ Upload to PyPI
python -m twine upload dist/*

# ✓ Wait 5-10 minutes for indexing

# ✓ Verify on PyPI
pip install ennam-django-apidog
```

## Lệnh Hữu Ích

```bash
# Xem phiên bản hiện tại
grep '^version' pyproject.toml

# Xem git tags
git tag -l

# Xem PyPI package info
curl https://pypi.org/pypi/ennam-django-apidog/json

# Xem upload history
python -m twine --version

# Kiểm tra wheel content
unzip -l dist/*.whl | head -20

# Kiểm tra sdist content
tar -tzf dist/*.tar.gz | head -20
```

## Các Tài Liệu Liên Quan

- [PUBLISH.md](PUBLISH.md) - Quick reference cho publishing
- [RELEASE.md](RELEASE.md) - Release process checklist
- [BUILD.md](BUILD.md) - Build infrastructure overview
- [PyPI Documentation](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)

## Support

Nếu gặp vấn đề:

1. Kiểm tra error message chi tiết
2. Xem troubleshooting section trên trang này
3. Xem logs của build
4. Tham khảo PyPI/Twine documentation
5. Thử test trên TestPyPI trước

**Happy Publishing! 🚀**
