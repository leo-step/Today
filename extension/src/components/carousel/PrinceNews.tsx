import Table from "react-bootstrap/Table";
import TodayLogo from "../../images/logo.png";
import React from "react";
import { useData } from "../../context/DataContext";
import { CarouselWidgetProps, CarouselHeader } from "../Carousel";
import { WidgetRow } from "../widget/WidgetRow";
import { EventTypes, useMixpanel } from "../../context/MixpanelContext";

type Article = {
  title: string;
  link: string;
};

function PrinceNewsTable(props: CarouselWidgetProps) {
  const data = useData();
  const mixpanel = useMixpanel()

  const articles: Article[] = data?.prince?.articles || [];

  const rows = articles.map((article, i) => {
    return (
      <WidgetRow key={i} props={{ index: i, data: articles }}>
        <a
          href={article.link}
          className="prince-a"
          style={{ textDecoration: "none" }}
          onClick={() => mixpanel.trackEvent(EventTypes.NEWS_CLICK, article)}
        >
          <b>{article.title}</b>{" "}
        </a>
      </WidgetRow>
    );
  });

  return (
    <div className="prince">
      <Table variant="dark" borderless>
        <tbody>
          <CarouselHeader props={props}>
            Today{" "}
            <img
              alt="Today"
              style={{ width: 40, marginLeft: 5, marginBottom: 8 }}
              src={TodayLogo}
            />{" "}
          </CarouselHeader>
          {rows}
        </tbody>
      </Table>
    </div>
  );
}

export default PrinceNewsTable;
