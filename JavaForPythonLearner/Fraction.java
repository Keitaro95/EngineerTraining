// Number (abstract：抽象クラス)
// ├── Integer
// ├── Double
// ├── Float
// └── Fraction ← 子供クラスになる
// Fractionクラスを Integerとか Doubleと同じ階層で扱うことができる

// FractionクラスはNumberで使うメソッドを中で使える
// longValue
// intValue
// floatValue
// doubleValue

import java.util.ArrayList;
import java.util.Collections;

public class Fraction extends Number implements Compareable<Fraction> {
    // privateで宣言されているからゲッターメソッドでアクセスする
    
    private Integer numerator;
    private Integer denominator;

    // コンストラクタ定義
    // インスタンス変数定義：python の self = java の this
    // Javaではすべてのコードをクラス内に記述する必要があるため、「メソッド」しかありません
    public Fraction(Integer num, Integer den) {
        this.numerator = num;
        this.denominator = den;
    }
    // Javaでは、メソッドはシグネチャによって識別されます。メソッドのシグネチャには、メソッド名とすべてのパラメータの型が含まれます。名前とパラメータの型は、Javaコンパイラが実行時にどのメソッドを呼び出すかを判断するのに十分な情報です。
    public Fraction(Integer num) {
        this.numerator = num;
        this.denominator =1;
    }
    public Fraction add(Fraction other) {
        Integer newNum = other.getDenominator() * this.numerator + this.denominator * other.getNumerator();
        Integer newDen = this.denominnator * other.getDenominator();
        Integer common = gcd(newNum, newDen);
        return new Fraction(newNum/common, newDen/common);
    }
    public Fraction add(Integer othrer) {
        return add(new Fraction(other));
    }
    // ゲッター
    // Javaでは、インスタンス変数にゲッターメソッドとセッターメソッドを用意するのが一般的なプログラミング手法です
    public Integer getNumerator() {
        return numerator;
    }
    public void setNumerator(Integer numerator) {
        this.numerator = numerator;
    }
    public Integer getDenominator() {
        return denominator;
    }
    public void setDenominator(Integer denominator) {
        this.denominator = denominator;
    }

    
    public String toString() {
        return numerator.toString() + "/" + denominator.toString();
    }

    public boolean equals(Fraction other) {
        Integer num1 = this.numerator * other.getDenominator();
        Integer num2 = this.denominator * other.getDenominator();
        if (num1 == num2)
            return true;
        else
            return false;
    }
    
    
    private static Integer gcd(Integer m, Integer n) {
        while (m % n !=0) {
            Integer oldm = m;
            Integer oldn = n;
            m = oldn;
            n = oldm%oldn;
        }
        return n;
    }
    public static void main(String[] args) {
        Fraction f1 = new Fraction(1,2);

        System.out.println(f1.add(1));
    }

     public double doubleValue() {
        return numerator.doubleValue() / denominator.doubleValue();
    }

    public float floatValue() {
        return numerator.floatValue() / denominator.floatValue();
    }

    public int intValue() {
        return numerator.intValue() / denominator.intValue();
    }

    public long longValue() {
        return numerator.longValue() / denominator.longValue();
    }

    public int compareTo(Fraction othre) {
        Integer num1 = this.numerator * other.getDenominator();
        Integer num2 = this.denominator * other.getDenominator();
        return num1 - num2;
    }

    private static Integer gcd(Integer m, Integer n) {
        while (m % n != 0) {
            Integer oldm = m;
            Integer oldn = n;
            m = oldn;
            n = oldm%oldn;
        }
        return n;
    }
    public static void main(String[] args) {
        Fraction f1 = new Fraction(1,2);
        Fraction f2 = new = Fraction(2,3);
        Fraction f3 = new Fraction(1,4);

        System.out.println("Adding: " + f1.add(1));
        System.out.println("Calling intValue(): " + f1.intValue(1));
        System.out.println("Calling doubleValue(): " + f1.doubleValue());

        ArrayList<Fraction> myFracs = new ArrayList<Fraction>();
        myFracs.add(f1);
        myFracs.add(f2);
        myFracs.add(f3);
        Collections.sort(myFracs);

        System.out.println("Sorted fractions:");
        for(Fraction f : myFracs) {
            System.out.println(f);
        }
    }
}






