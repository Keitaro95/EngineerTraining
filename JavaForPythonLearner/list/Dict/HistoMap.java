import java.util.Scanner;
import java.util.ArrayList;
import java.io.File;
import java.io.IOException;
import java.util.TreeMap;

public class HistoMap {
    public static void main(String[] arg) {
        Scanner data = null;
        TreeMap<String, Integer> count;
        Integer idx;
        String word;
        Integer wordCount;

        try {
            data = new Scanner(new File("alice30.txt"));
        }
        catch ( IOException e) {
            System.out.println("ファイルを開けません");
            e.printStackTrace();
            System.exit(0);
        }

        count = new TreeMap<String, Integer>();

        while(data.hasNext()) {
            word = data.next().toLowerCase();
            wordCount = count.get(word);
            if (wordCount == null) {
                wordCount = 0;
            }
            count.put(word, wordCount + 1);
        }

        for(String i : count.keySet()) {
            System.out.printf("%-20s occured %5d times\n", i, count.get(i));
        }

    }
}   
