import java.util.Scanner;
import java.util.ArrayList;
import java.io.File;
import java.io.IOException;

public class Histo {

    public static void main(String[] arg) {
        // 変数を宣言
        Scanner data = null;
        // ここ大事
        ArrayList<Integer> count;
        Integer idx;

        try {
            data = new Scanner(new File("test.dat"));
        }
        // javaではこんなふうにerrorキャッチを何個も書くのがベター
        catch ( IOException e) {
            System.out.println("Unable to open data file");
            e.printStackTrace();
            System.exit(0);
        }
        count = new ArrayList<Integer>(10);
        for (Integer i = 0; i < 10; i++) {
            // Pythonの [0] * 10 に相当する書き方
            // インデックス i の位置に 0 を挿入
            count.add(i,0); 
        }

        // ファイルからデータを読み込むための典型的なJavaパターン
        while(data.hasNextInt()) {
            // 整数を読み取ってidxに代入
            idx = data.nextInt();
            // idxの値を取ってきて+1する。その値をidxに上書き
            // count[idx] += 1  # Python
            // javaではインデックスのメソッドが必要になる
            count.set(idx, count.get(idx)+1);
        }

        idx = 0;
        // for i in countと同じ
        for(Integer i : count) {
            System.out.println(idx + " occured " + i + " times.");
            idx++;
        }
        
    }

}