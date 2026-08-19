# Anh Docker de tai lap ket qua trong moi truong co lap hoan toan.
# Kho khong co dependency runtime, nen anh nay chi la Python + ma nguon.
#
#   docker build -t dra-research .
#   docker run --rm dra-research                      # chay toan bo kiem dinh + test
#   docker run --rm dra-research make all             # sinh lai file dan xuat
#   docker run --rm -v "$PWD/out:/repo/out" dra-research \
#       python tools/baseline_router.py --mode lodo

FROM python:3.12-slim

# make can cho cac tac vu trong Makefile; ngoai ra khong cai them gi.
RUN apt-get update \
    && apt-get install --no-install-recommends -y make \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

WORKDIR /repo
COPY . /repo

# Kiem tra ngay khi build: anh chi build thanh cong neu du lieu hop le.
RUN python tools/validate_datasets.py --strict

CMD ["make", "check"]
