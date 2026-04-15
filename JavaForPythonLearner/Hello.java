// 1. 全てのJavaプログラムはクラスを定義する必要がある。全てのコードはクラス内に記述されます。{}の中にコードを書いていくよ
public class Hello {
    // 2. javaの全てには型を持つ必要があります

    // 3. 全てのJavaプログラムにはこのようなメソッド定義を持つ必要があります

    // public: このメソッドは誰でも呼び出せるメソッドですよ。(他に protected, privateがある)

    // static：インスタンス不要でメソッドを呼び出せるよ
    // pythonだとインスタンスを作って呼び出すものだけど、javaだと Hello.main(param1) のようにインスタンス化せず呼び出せるよ


    // void： pythonでreturn文を省略するように、このメソッドは値を返さない、という意味。この場合、void(空)の型を返すということになる

    // main：関数の命名

    // String[]：パラメーターargsは文字型の配列ですよ　　
    public static void main(String[] args) {


        // System：標準出力
        // out：standard out
        // ; でプログラム終了を告げる。これがないとプログラムが終了したと告げられない。
        System.out.println("Hello World");
    }
}

