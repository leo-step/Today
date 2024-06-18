import React from "react";

type HeaderProps = {
  title: string;
};

const WidgetHeader = (props: HeaderProps) => {
  return (
    <tr>
      <td colSpan={3}>
        <h3 style={{ fontWeight: "bold" }}>{props.title}</h3>
      </td>
    </tr>
  );
};

export default WidgetHeader;
