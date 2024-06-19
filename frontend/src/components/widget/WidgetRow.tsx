import React from "react";
import { useTheme } from "../../context/ThemeContext";

type RowData = {
  index: number;
  data: any[];
};

type RowProps = {
  children: React.ReactNode;
  props: RowData;
};

export const WidgetRow: React.FC<RowProps> = ({ children, props }) => {
  const theme = useTheme();
  const { index, data } = props;

  return (
    <tr
      className={index === data.length - 1 ? "divider no-divider" : "divider"}
      style={{ borderBottomColor: theme.accent }}
      key={index}
    >
      <td colSpan={3}>
        <div className="row-content">{children}</div>
      </td>
    </tr>
  );
};
