import Table from "react-bootstrap/Table";

function PrinceNewsTable() {
  const dummyText = [
    "After visual arts professor used n-word in seminar, Princeton finds no violation of policy.",
    "Fintan O’Toole warns of the danger of ‘aestheticized politics’ in campus talk.",
    "University officially announces new upperclass student dining pilot.",
  ];

  return (
    <div
      style={{
        "padding-left": "20px",
        "padding-right": "20px",
        "padding-top": "10px",
        "padding-bottom": "10px",
        "border-radius": "25px",
        "background-color": "#212529",
        width: "700px",
      }}
    >
      <Table variant="dark" borderless>
        <tbody>
          <tr className="centered">
            <td>
              {" "}
              <h1>The Prince 🗞️</h1>
            </td>
          </tr>
          <div
            style={{
              "padding-top": "10px",
              "padding-bottom": "10px",
              "border-bottom-style": "solid",
              "border-bottom-color": "#FF2A0D",
              "border-bottom-width": "thin",
            }}
          >
            <tr>
              <td> {dummyText[0]}</td>
            </tr>
          </div>
          <div
            style={{
              "padding-top": "10px",
              "padding-bottom": "10px",
              "border-bottom-style": "solid",
              "border-bottom-color": "#41EAEA",
              "border-bottom-width": "thin",
            }}
          >
            <tr>
              <td> {dummyText[1]}</td>
            </tr>
          </div>
          <div style={{ "padding-top": "10px", "padding-bottom": "10px" }}>
            <tr>
              <td> {dummyText[2]}</td>
            </tr>
          </div>
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
