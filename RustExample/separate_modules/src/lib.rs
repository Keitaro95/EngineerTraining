mod front_of_house;

pub use create::front_of_house::hosting;

pub fn eat_at_restaurant() {
    hosting::add_to_waitlist();
}