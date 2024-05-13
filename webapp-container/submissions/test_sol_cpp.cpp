#include <iostream>
#include <iomanip>

using namespace std;

int main(){
	long double a, b;
	cin >> a >> b;
	
	cout << fixed << setprecision(20) << a+b;
}
