// Template Method



// アルゴリズムの骨組みをスーパークラスで固定する
abstract class DataImporter {

    // このテンプレートを使ったクラスは全てこの動き
    public import(source: string): void {
        const raw = this.read(source);
        const records = this.parse(raw);

        if (this.shouldValidate()) {
            this.validate(records);
        }
        this.save(records);
        console.log(`${records.length} 件を取り込みました`);
    }

    // 内部メソッド
    protected abstract read(source: string): string;
    protected abstract parse(raw: string): Record<string, unknown>[];

    protected shouldValidate(): boolean {
        return true;
    }

    protected validate(records: Record<string, unknown>[]): void {
        if (records.length === 0) throw new Error("レコードが空です");
    }

    protected save(records: Record<string, unknown>[]): void {
        console.log("DBに保存:", records);
    }
}

class CsvImporter extends DataImporter {
    protected read(source: string): string {
        return "id,name,alice,bob";
    }
    protected parse(raw: string): Record<string, unknown>[] {
        const [header, ...rows] = raw.split("\n");
        const keys = header.split(",");
        return rows.map(r => Object.fromEntries(r.split(",").map((v, i) => [keys[i], v])));
    }
}

class JsonImporter extends DataImporter {
  protected read(source: string): string {
    return '[{"id":1,"name":"Carol"}]';
  }
  protected parse(raw: string): Record<string, unknown>[] {
    return JSON.parse(raw);
  }
  // フックを上書きしてバリデーションをスキップ
  protected shouldValidate(): boolean {
    return false;
  }
}

console.log(new CsvImporter().import("users.csv"))
console.log(new JsonImporter().import("users.json"))