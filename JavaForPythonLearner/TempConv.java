import java.util.Scanner; // ここで宣言してコード内でScanner単独で使う
// importを書かなくても Scanner→java.util.Scanner　に置き換えれば通る
public class TempConv {
    public static void main(String[] args) {
        // Javaで大事なのはまず変数と変数の型を宣言する

        // 大文字の型宣言なのでこれはObjectの宣言
        Double fahr;
        Double cel; // ここをコメントアウトするとエラーが出る
        Scanner in;
        
        // Scanner がバイト列を解析（パース）して、扱いやすい型に変換
        in = new Scanner(System.in);
        System.out.println("Enter the temperature in F: ");
        // double で受け取りたい → inをnextDouble()変換する
        // Javaは型に厳しい言語なので、宣言した型と合わないとコンパイラが弾きます。
        fahr = in.nextDouble();

        cel = (fahr -32) * 5.0/9.0;
        System.out.println("The temperatur in C is: " + cel);
    }
}