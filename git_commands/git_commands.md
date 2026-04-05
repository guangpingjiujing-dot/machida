# git・GitHubとは

## git 
- 変更管理ツール
- ゲームでいうところのセーブポイント(commit)を無限につくれる
- SFチックに言うとタイムリープとか世界線(branch)の移動が可能
- もっと言うと別世界線で起こした変更を元の世界線に反映(merge)することが可能
- gitはあくまでローカルのツールであり、GitHubをもし使わなかったらその変更管理は自分のPCの中にしかない

## GitHub
- gitのハブ
- チームで共有できるgit用ファイルサーバー
- 自分のgit管理している変更履歴を他人に共有できる

## git comands

### コマンドで覚えた方が楽  
git --version  
git init  
git remote --v  
git remote add origin <gitのurl>  
git clone <gitのurl> (これはエディタからでもいいかも)  
git pull origin main  

### エディタからやった方が楽  
git add  
git commit  
git push  
git checkout -b <ブランチ名>  