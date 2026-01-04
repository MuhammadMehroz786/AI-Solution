# Gmail SMTP Setup Guide for CSV Email

## Step 1: Generate Gmail App Password

### Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Under "Signing in to Google", enable **2-Step Verification**
4. Follow the setup instructions

### Create App Password
1. After enabling 2FA, go back to **Security**
2. Under "Signing in to Google", click **App passwords**
3. Click **Select app** → Choose **Mail**
4. Click **Select device** → Choose **Other (Custom name)**
5. Enter name: `Dream 100 Railway`
6. Click **Generate**
7. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

## Step 2: Update .env File

Edit your `.env` file and add your Gmail credentials:

```env
# SMTP Configuration for Gmail
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-actual-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

**Important:**
- `SMTP_USER`: Your full Gmail address
- `SMTP_PASSWORD`: The 16-character app password (remove spaces)
- `BATCH_RESULTS_EMAIL`: The email where you want to receive CSV files

**Example:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=mehroz.muneer@gmail.com
SMTP_PASSWORD=xyzw abcd efgh ijkl
BATCH_RESULTS_EMAIL=mehroz.muneer@gmail.com
```

## Step 3: Test Email Sending

Run the test script:

```bash
cd "/Users/apple/Desktop/Bot/Mario - N8N"
python test_smtp_email.py
```

This will send a test email with a sample CSV attachment.

## Step 4: Deploy to Railway

When deploying to Railway, add these environment variables:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
BATCH_RESULTS_EMAIL=mehroz.muneer@gmail.com
```

## How It Works

### Complete Flow:

```
1. User uploads CSV with multiple prospects
   ↓
2. Flask processes each prospect individually
   - Scrapes website
   - Analyzes with Manus AI
   - Generates 2 documents with OpenAI
   - Sends to N8N for Google Doc creation
   ↓
3. N8N creates Google Docs and sends callback
   ↓
4. Flask collects all document URLs
   ↓
5. Flask generates CSV with all results
   ↓
6. Flask sends email via SMTP with CSV attachment
   ✅ Email delivered to mehroz.muneer@gmail.com
```

## Email Features

The email includes:

✅ **Subject**: Dream 100 Batch Processing Results - [Date/Time]

✅ **Body**:
- Professional HTML format
- Summary of batch processing
- List of what's included in CSV
- Batch ID for tracking

✅ **Attachment**:
- CSV file: `dream100_results_YYYYMMDD_HHMMSS.csv`
- Contains all company data + document links

## Troubleshooting

### Error: "SMTP authentication failed"
**Solution**:
- Make sure you're using an **App Password**, not your regular Gmail password
- Check that 2-Factor Authentication is enabled
- Verify the app password has no spaces

### Error: "SMTPSenderRefused"
**Solution**:
- Verify `SMTP_USER` is your full Gmail address
- Make sure the email is verified in your Google Account

### Error: "Connection refused"
**Solution**:
- Check `SMTP_HOST` is `smtp.gmail.com`
- Check `SMTP_PORT` is `587`
- Verify your network allows outbound SMTP connections

### Railway-Specific Issues

**Port blocking**: Railway allows SMTP on port 587 ✅

**Environment variables**: Make sure all SMTP variables are set in Railway dashboard

**Logs**: Check Railway logs for detailed SMTP error messages

## Security Best Practices

1. ✅ **Never commit `.env` to git**
2. ✅ **Use app passwords, not regular passwords**
3. ✅ **Rotate app passwords periodically**
4. ✅ **Use environment variables in production**
5. ✅ **Monitor Gmail activity for unauthorized access**

## Testing Checklist

- [ ] 2-Factor Authentication enabled on Gmail
- [ ] App password generated
- [ ] `.env` file updated with SMTP credentials
- [ ] Test email sent successfully
- [ ] CSV attachment received
- [ ] CSV file opens correctly
- [ ] Document links work
- [ ] Ready for Railway deployment

## Next Steps

Once SMTP is working:
1. Deploy to Railway
2. Add SMTP environment variables to Railway
3. Test batch processing end-to-end
4. Verify CSV emails are delivered
5. Production ready! 🚀
