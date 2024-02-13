import Table from "react-bootstrap/Table";

function Valentines() {

  return (
    <div className="sneaky-links">
      <Table variant="dark" borderless>
        <tbody>
          <tr>
            <td>
              {" "}
              <h3 style={{ fontWeight: "bold", color: "hotpink" }}>💖   Happy Valentine's Day!   💖</h3>
            </td>
            <td></td>
          </tr>
          <tr>
            <td>
              <h5>To our first users, thanks for being the backbone of our extension. 
                We’re giving out Valentine’s goody bags to say we love you: <br/>
                <a href="https://forms.gle/oqbKUT4PGEMrfEhP7" className="valentine-a"
                  >Fill out this quick form to get yours.</a>
                </h5>
            </td>
          </tr>
        </tbody>
      </Table>
    </div>
  );
}

export default Valentines;
