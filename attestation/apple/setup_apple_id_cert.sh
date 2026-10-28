#!/bin/bash
set -e

# ================= 配置区 =================
# 依然使用你之前的自定义 AAGUID
AAGUID_HEX="0a751f62c26544568aeb1bdece76f97c"
# ==========================================

echo "=================================================="
echo "🔮 开始为 FIDO2Applet 生成 Apple ID 兼容证书..."
echo "=================================================="

# 1. 动态生成符合 Apple 胃口的 openssl.ext
cat << EOF > openssl.ext
[fido2_ext]
basicConstraints = CA:FALSE
keyUsage = critical, digitalSignature
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
1.3.6.1.4.1.45724.1.1.4 = ASN1:FORMAT:HEX,OCTETSTRING:${AAGUID_HEX}
EOF

# 2. 用 OpenSSL 签署证书链
# 生成自签名根 CA
openssl ecparam -name prime256v1 -genkey -noout -out ca.key
openssl req -new -x509 -key ca.key -out ca.crt -subj "/CN=Jesse Fake Root CA" -days 3650

# 生成用于虚拟卡响应的 Batch（批次）密钥
openssl ecparam -name prime256v1 -genkey -noout -out batch.key
openssl req -new -key batch.key -out batch.csr -subj "/CN=FIDO2 Applet Batch"

# 【核心】用根 CA 签名 Batch 凭据，并注入 AAGUID 扩展
openssl x509 -req -in batch.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -out batch.crt -days 3650 -extfile openssl.ext -extensions fido2_ext

# 将 PEM 格式的证书和私钥转换为纯二进制 DER 格式，方便提取干净的 Base64
openssl x509 -in batch.crt -outform DER -out batch.der
openssl ec -in batch.key -outform DER -out batch_key.der 2>/dev/null

echo "📊 正在将证书与私钥抽取为纯净的一行 Base64..."
# 提取单张证书和私钥的纯净 Base64（删掉所有换行符）
CERT_B64=$(base64 -w 0 batch.der)
KEY_B64=$(base64 -w 0 batch_key.der)

echo "--------------------------------------------------"
echo "🎉 生成成功！下面是你可以直接复制并运行的安装命令："
echo "--------------------------------------------------"
echo ""
echo "python3 install_attestation_cert.py \\"
echo "  --aaguid ${AAGUID_HEX} \\"
echo "  --ca-cert-bytes \"${CERT_B64}\" \\"
echo "  --ca-private-key \"${KEY_B64}\""
echo ""
echo "--------------------------------------------------"

# 清理临时垃圾文件
rm -f openssl.ext ca.key ca.crt batch.csr batch.crt batch.der batch_key.der batch.key ca.srl
