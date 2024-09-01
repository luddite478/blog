openssl req -x509 -newkey rsa:4096 -keyout haproxy.key -out haproxy.crt -days 365 -nodes -subj "/C=Us"

cat haproxy.crt > fullchain.pem
cat haproxy.key >> fullchain.pem
base64 -w 0 fullchain.pem > haproxy-fullchain.pem.base64

echo "" >> .haproxy.env
echo "HAPROXY_FULLCHAIN_BASE64=$(cat haproxy-fullchain.pem.base64)" >> .haproxy.env
rm haproxy.crt haproxy.key haproxy-fullchain.pem.base64