use fancy_regex::Regex;
use pyo3::prelude::*;


#[pyfunction]
fn parse(   
    exceptions: Vec<String>,
    website_text: Vec<String>,
) -> PyObject {
    let email_regex: Regex = Regex::new(r"\S+@\S+\.\S+").unwrap();
    let password_regex: Regex = Regex::new(r"\S*\d\S*").unwrap();

    let mut login: &str = "";
    let mut password: &str = "";

    for (i, current) in website_text.iter().enumerate() {
        match email_regex.find(current).unwrap() {
            Some(value) => 
                login = if !exceptions.contains(&value.as_str().to_string()) {
                    value.as_str()
                } else {
                     continue
                },
            None => continue
        }

        // If the login was found
        if login.contains(":") { 
            let index: usize = login.find(":").unwrap();
            password = &login[index+1..];
            login = &login[..index];
            break
        } else {
            for k in 1..4 {
                match password_regex.find(website_text[i+k].as_str()).unwrap() {
                    Some(value) => { 
                        password = value.as_str();
                        break
                    },
                    None => continue
                }
            }
        }
    }
    
    return Python::with_gil(|py| {
        vec![login, password].to_object(py)
    })
}


#[pymodule]
fn rust_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse, m)?)?;
    Ok(())
}
