#include <bits/stdc++.h>
#include <climits>
using namespace std;

// bool isSatisFactory(vector<int> &a, int n){
// 	int speed = 1;
// 	for(int i=1;i<n;i++){
// 		int x = a[i];
// 		int y = a[i-1];
// 		speed = (y/x)*speed;
// 	}
// 	return speed == 1;
// }

// bool solve(vector<int> &a, int n){

// }

// bool solve(int a, int b, int c, int d){
// 	c -= a;
// 	d -= b;
// 	if(b>a){
// 		int t = a;
// 		a = b;
// 		b = t;
// 	}
// 	if(d>c){
// 		int t = c;
// 		c = d;
// 		d = t;
// 	}
// 	while(b--){
// 		a-=2;
// 	}
// 	while(d--){
// 		c-=2;
// 	}
// 	return (a<3 && c<3);
// }

// int countNeat(vector<int> &a, int n){
// 	unordered_map<int, int> blocks;
// 	for(int i=0;i<n;i++){
// 		blocks[a[i]]++;
// 	}
// 	for(int i=0;i<n;i++){

// 	}
// }

// int find(vector<int> &a, unordered_map<int, int> &freq){
// 	for(int i=0;i<a.size();i++){
// 		if(freq[a[i]] == 1) return i;
// 	}
// 	return -1;
// }\

// int even(int x){
// 	return x/2;
// }

// pair<int,int> solve(vector<int> &a, int n){
// 	if(a.size() <= 2){
// 		return {0,0};
// 	}
// 	vector<int> prefixSum(n, 0);
// 	prefixSum[0] = a[0];
// 	for(int i=1;i<n;i++){
// 		prefixSum[i] = a[i]+prefixSum[i-1];
// 	}
// 	for(int l = 1;l<n;l++){
// 		for(int r=l+1;r<n;r++){
// 			int s1 = prefixSum[l-1];
// 			s1 %= 3;
// 			int s2 = prefixSum[r-1] - prefixSum[l-1];
// 			s2 %= 3;
// 			int s3 = prefixSum[n-1] - prefixSum[r-1];
// 			s3 %= 3;
// 			if((s1 != s2 && s1 != s3 && s2 != s3) || (s1 == s2 && s1 == s3)) return {l,r};
// 		}
// 	}
// 	return {0,0};
// }

// bool isSorted(vector<int> &a, int n){
// 	for(int i=1;i<n;i++){
// 		if(a[i] > a[i-1]) return false;
// 	}
// 	return true;
// }

// int compute_cost(vector<int> &a, int n) {
//     int left = -1, right = -1;
//     for(int i=0;i<n;i++){
//         if(a[i] != i+1){
//             if(left==-1) left=i;
//             right=i;
//         }
//     }
//     if(left==-1) return 0; // already sorted
//     return right-left+1;
// }

// int solve(vector<int> &a, int n){
// 	vector<bool> present(n+1, false);
// 	for(int x : a) if(x) present[x] = true;
// 	vector<int> missing;
// 	for(int i=1;i<=n;i++){
// 		if(!present[i]) missing.push_back(i);
// 	}

// 	int l=0,r = missing.size()-1;
// 	for(int i=0;i<n;i++){
// 		if(a[i] == 0){
// 			if(i<n/2) a[i] = missing[r--];
// 			else a[i] = missing[l++];
// // 		}
// // 	}

// // 	return compute_cost(a, n);
// // }

// // bool isNonDescending(vector<int> &a, vector<int> &b, int n){
// // 	for(int i=1;i<n;i++){
// // 		if(a[i] < a[i-1] || b[i] < b[i-1]) return false;
// // 	}
// // 	return true;
// // }

// // // void solve(vector<int> &a, vector<int> &b, int n, int i, long long &c){
// // // 	swap(a[i], b[i]);
// // // 	if(isNonDescending(a, b, n)){
// // // 		c++;
// // // 		c = c % 998244353;
// // // 	}
// // // 	solve(a, b, n, i+1);
// // // 	swap(a[i], b[i]);
// // // }

// // bool isBal(vector<int> &a, int n, int i, int j){
// // 	if(i >= j) return true;
// // 	int c = 0, p = i+1;
// // 	unordered_map<int, int> freq;
// // 	for(int k=i;k<=j;k++){
// // 		freq[a[k]]++;
// // 	}
// // 	c = freq[a[i]];

// // 	for(auto &kv : freq){
// // 		if(kv.second != c) return false;
// // 	}
// // 	return true;
// // }

// // // struct Block{
// // // public:
// // // 	int value;
// // // 	int count;
// // // }

// // int solve(vector<int> &a, int n){

// // 	vector<Block> blocks;
// // 	int cnt = 1;
// // 	for(int i=1;i<n;i++){
// // 	    if(a[i]==a[i-1]) cnt++;
// // 	    else{
// // 		        blocks.push_back({a[i-1], cnt});
// // 		        cnt = 1;
// // 	    }

// // 	}
// // blocks.push_back({a[n-1], cnt}); // last block

// // 	vector<int> ans;
// // 	if(!a.size()) return 0;

// // 	for(int i=0;i<n;i++){
// // 		for(int j=i;j<n;j++){
// // 			if(isBal(a, n, i, j) && j-i+1 > int(ans.size())){
// // 				ans = {};
// // 				for(int k=i;k<=j;k++){
// // 					ans.push_back(a[k]);
// // 				}
// // 			}
// // 		}
// // 	}

// // 	return ans.size();
// // }

// int main(){
// 	int t;
// 	cin>>t;
// 	while(t--){
// 		int n,m;
// 		cin>>n>>m;
// 		vector<int> ans(m);
// 		for(int i=0;i<m;i++){
// 			ans[i] = i+1;
// 		}
// 		vector<int> a(n);
// 		bool solved = false;
// 		for(int i=0;i<n;i++){
// 			if(!solved){
// 				int l;
// 				cin>>l;
// 				vector<int> s(l);
// 				bool dt = false;
// 				for(int k=0;k<l;k++){
// 					cin>>s[k];
// 					if(ans[s[]]) ans[i] = 0;
// 					if(dt){
// 						solved = true;
// 						break;
// 					}
// 					for(int e = 0;e<m;e++){
// 						if(a[e]){
// 							break;
// 						}
// 						dt = true;
// 					}
// 				}
// 			}
// 		}

// 		if(solved) cout<<"YES"<<endl;
// 		else cout<<"NO"<<endl;
// 	}
// }

// vector<vector<int> > dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

// void dfs(int n, int k, vector<vector<int> > &visited, vector<string> &strs){
// 	if(k<n)
// 	if(n<0 || n>=)
// }

// int win(int &winners, int &losers, vector<vector<int> > &dw){
// 	int i=winners, j = losers;
// 	if(dw[i][j] != -1) return dw[i][j];
// 	if(winners == 1) return 1;
// 	if(winners % 2) winners = winners/2+1;
// 	else winners = winners/2;
// 	losers += winners/2;
// 	dw[i][j] = 1+win(winners, losers, dw);
// 	return dw[i][j];
// }

// int lose(int &losers, vector<int> &dl){
// 	int t = losers;
// 	if(dl[t] != -1) return dl[t];
// 	if(losers == 1) return 1;
// 	if(losers%2) losers -= losers/2-1;
// 	else losers -= losers/2;
// 	dl[t] = 1+lose(losers, dl);
// 	return dl[t];
// }

// int solve(int n){
// 	if(n == 2) return 2;
// 	bool isOdd = false;
// 	if(n%2) isOdd = true;
// 	int winners, losers;

// 	if(isOdd)
// 		winners = n/2 + 1;

// 	else winners = n/2;

// 	losers = n - winners;
// 	vector<int> dl(n, -1);
// 	vector<vector<int> > dw(n, vector<int>(n, -1));

// 	return win(winners, losers, dw) + lose(losers, dl)+1;
// }

// long long solve(int n){
// 	if(n<=2) return 0;

// 	int m1 = solve()
// }

// string solve(vector<int> &a, vector<pair<int, int> > intervals, int m , int n){
// 	string ans(n, '1');
// 	vector<int> interval_min(m), interval_max(m);
// 	for(int i=0;i<m;i++){
// 		int l = intervals[i].first - 1, r = intervals[i].second - 1;
// 		int mn = a[l], mx = a[l];
// 		for(int j=l;j<=r;j++){
// 			mn = min(mn, a[j]);
// 			mx = max(mx, a[j]);
// 		}
// 		interval_min[i] = mn;
// 		interval_max[i] = mx;
// 	}

// 	for(int x=1;x<=n;x++){
// 		bool valid = true;
// 		for(int i=0;i<m;i++){
// 			if((x-interval_min[i])*(x-interval_max[i]) < 0){
// 				valid = false;
// 				break;
// 			}

// 		}

// 		if(!valid) ans[x-1] = '0';
// 	}

// 	return ans;
// }

// void solve(int n, int k, vector<vector<char>> &board){
// 	if(k == n*n-1){
// 		cout<<"NO";
// 		return;
// 	}

// 	for(int i=0;i<n;i++){
// 		for(int j=0;j<n;j++){
// 			if(k){
// 				board[i][j] = 'U';
// 				k--;
// 				continue;
// 			}

// 			if(j != n-1){
// 				board[i][j] = 'D';
// 			}

// 			if(i == 0) board[i][j] = 'R'
// 		}
// 	}

// }

// int solve(int n, int k, vector<int> &a){
// 	int z = 0, c = 0;
// 	vector<int> f(k, 0);
// 	for(int i=0;i<n;i++){
// 		if(a[i] == k)c++;
// 		if(a[i] < k) f[a[i]]++;
// 	}
// 	for(int i=0;i<k;i++){
// 		if(!f[i]) z++;
// 	}
// 	return max(c, z);
// }

// bool solve(vector<vector<int> > &a, int n, int m){
// 	if(n<=1) return false;

// 	int valid = 0;

// }

// oid solve(vector<int> a){
// 	if(a[0] == a[1] &&
// 		a[1]== a[2] &&
// 		a[2]== a[3]) cout<<"YES\n";
// 	else cout<<"NO\n";
// }v

// void solve(vector<char> &s, vector<char> &t){
// 	vector<int> f(26, 0);
// 	for(char ch:s){
// 		int val = ch - 'a';
// 		f[val]++;
// 	}
// 	for(char ch:t){
// 		int val = ch - 'a';
// 		f[val]--;
// 		if(f[val]<0){
// 			cout<<"NO"<<endl;
// 			return;
// 		}
// 	}

// 	for(int i=0;i<26;i++){
// 		if(f[i]){
// 			cout<<"NO"<<endl;
// 			return;
// 		}
// 	}
// 	cout<<"YES"<<endl;
// }

int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        cin >> n;
        vector<int> a(n);
        for (int i = 0; i < n; i++)
            cin >> a[i];
        sort(a.begin(), a.end());
        for (int val : a)
            cout << val << " ";
        cout << endl;
    }
}