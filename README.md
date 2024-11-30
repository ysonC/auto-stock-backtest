## Step 1 ##
- Update and download dependencies
sudo apt update
sudo apt install -y libnss3 libxss1 libappindicator3-1 libasound2

- Download google-chrom
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

- Fix Any Dependency Issues
sudo apt --fix-broken install

- Download chromedriver and place it in the path
https://googlechromelabs.github.io/chrome-for-testing/#stable


