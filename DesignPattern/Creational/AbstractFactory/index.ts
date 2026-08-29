
// テーマを切り替えると、ボタンもチェックボックスも切り替わる

// 抽象インターフェース
interface Button { render(): string }
interface Checkbox { render(): string }


// 具体的な製品
class DarkButton implements Button { render() { return "dark button" }}
class DarkCheckbox implements Checkbox { render() { return "dark checkbox" }}
class LightButton implements Button { render() { return "light button" }}
class LightCheckbox implements Checkbox { render() { return "light checkbox" }}


// uiを作る抽象的な工場
interface UIFactory {
    createButton(): Button;
    createCheckbox(): Checkbox;
}

class DarkFactory implements UIFactory {
    createButton(): Button {
        return new DarkButton()
    }
    createCheckbox(): Checkbox {
        return new DarkCheckbox()
    }
}

class LightFactory implements UIFactory {
    createButton(): Button {
        return new LightButton()
    }
    createCheckbox(): Checkbox {
        return new LightCheckbox()
    }
}

// type: UIFactory を引数にとる。なので、黒テーマなら黒テーマの工場になる
function buildScreen(factory: UIFactory) {
    console.log(factory.createButton().render());
    console.log(factory.createCheckbox().render());
}
// このクラスは抽象化されているので
// 黒・白の工場をなんでも入れられる
// 欠点：新しい製品種（例：Slider）を追加すると、全ファクトリの修正が必要
// だからあまりいいとは言えないかも


buildScreen(new DarkFactory()); // Darkファクトリーを使ってスクリーンを作る
buildScreen(new LightFactory());