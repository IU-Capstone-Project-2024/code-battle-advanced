import java.util.Scanner;
import java.math.BigDecimal;

public class test_sol_java {
	public static void main (String[] args) {
		Scanner sc = new Scanner(System.in);
		BigDecimal a = new BigDecimal(sc.next());
		BigDecimal b = new BigDecimal(sc.next());
		
		a = a.add(b);
		System.out.printf("%.20f\n", a);
	}
}
