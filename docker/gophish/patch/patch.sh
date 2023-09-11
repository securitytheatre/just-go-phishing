# Stripping X-Gophish 
sed -i 's/X-Gophish-Contact/X-Contact/g' /build/models/maillog.go
sed -i 's/X-Gophish-Contact/X-Contact/g' /build/models/maillog_test.go
sed -i 's/X-Gophish-Contact/X-Contact/g' /build/models/email_request.go
sed -i 's/X-Gophish-Contact/X-Contact/g' /build/models/email_request_test.go
# Stripping X-Gophish-Signature
sed -i 's/X-Gophish-Signature/X-Signature/g' /build/webhook/webhook.go
# Changing servername
sed -i 's/const ServerName = "gophish"/const ServerName = "Microsoft Outlook 16.0"/' /build/config/config.go
# Changing rid value
# https://be.smart.com/common/oauth2/v2.0/authorize?client_id=4765445b-32c6-49b0-23e6-1d9376a276ca
sed -i 's/const RecipientParameter = "rid"/const RecipientParameter = "client_id"/g' /build/models/campaign.go

# Patch phish.go 404.html
cp "/patch/404.html" "/build/templates/"
patch /build/controllers/phish.go < /patch/phish.go.patch
