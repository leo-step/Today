import Canvas from "../images/canvas.png";
import Docs from "../images/google-docs.png";
import Gmail from "../images/gmail.png";
import GCal from "../images/gcal.png";
import {Button, Form, Modal} from "react-bootstrap"
import {useState} from "react";
import React from "react";
import { FiEdit2 } from "react-icons/fi";
// import WidgetHeader from "./widget/WidgetHeader";
import { EventTypes, useMixpanel } from "../context/MixpanelContext";
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Image from 'react-bootstrap/Image';
import Row from 'react-bootstrap/Row';
import { StorageKeys, useStorage } from "../context/StorageContext";



let selectedIcon = 0;

const LINKS = [
  "https://canvas.princeton.edu/", "https://mail.google.com/", "https://calendar.google.com/", "https://docs.google.com/"
  ];

type SneakyLink = {
  href: string;
  pos: number;
  id: string;
  alt: string;
  src: string;
  style?: React.CSSProperties;
};

// const storage = useStorage();


const initialSneakyLinks: SneakyLink[] = [
  {
    href: LINKS[0],
    pos: 0,
    id: "canvas",
    alt: "Canvas",
    src: Canvas,
  },
  {
    href: LINKS[1],
    pos: 1,
    id: "gmail",
    alt: "Gmail",
    src: Gmail,
    style: { paddingTop: "8px" },
  },
  {
    href: LINKS[2],
    pos: 2, 
    id: "gcal",
    alt: "GCal",
    src: GCal,
  },
  {
    href: LINKS[3],
    pos: 3,
    id: "docs",
    alt: "Docs",
    src: Docs,
  },
];

function SneakyLinksTable() {
  const storage = useStorage();

  const getBase64Data = (imageUrl: string): Promise<string> => {
    return new Promise((resolve, reject) => {
      fetch(imageUrl)
        .then((response) => response.blob())
        .then((blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve(reader.result as string);
          };
          reader.onerror = reject;
          reader.readAsDataURL(blob);
        })
        .catch(reject);
    });
  };

  

function httpify(url: string) {
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    return 'https://' + url;
  }
  return url;
}

function checkUrl(url: string) {
  const pattern =
  /(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?\/[a-zA-Z0-9]{2,}|((https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z]{2,}(\.[a-zA-Z]{2,})(\.[a-zA-Z]{2,})?)|(https:\/\/www\.|http:\/\/www\.|https:\/\/|http:\/\/)?[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}\.[a-zA-Z0-9]{2,}(\.[a-zA-Z0-9]{2,})?/g;
  return pattern.test(url);
}


const handleUpdate = async (e: React.FormEvent<HTMLFormElement>) => { 
    e.preventDefault();
    let newUrl = (document.getElementById('url-update') as HTMLInputElement).value;
    console.log(newUrl);

    if(newUrl === "") {
      newUrl = "https://canvas.princeton.edu/";
    }

    if(!checkUrl(newUrl)) {
      alert("Invalid URL");
      return;
    }

    newUrl = httpify(newUrl);
    
    let imageUrl = "https://logo.clearbit.com/" + newUrl;
    console.log(imageUrl);
    const updatedLinks = [...JSON.parse(sneakyLinks)];
    updatedLinks[selectedIcon].href = newUrl;
    if(isImageUploaded) {
      updatedLinks[selectedIcon].src = JSON.parse(sneakyLinks)[selectedIcon].src;
    }
    
    else {
      try {
        const base64data = await getBase64Data(imageUrl);
        updatedLinks[selectedIcon].src = base64data;
      } catch (error) {
        console.error("Error fetching image or converting to base64", error);
        alert("Error updating the icon image.");
        return;
      }
    }
    console.log("Update forced!");
    setSneakyLinks(JSON.stringify(updatedLinks));
    storage.setLocalStorage(StorageKeys.LINKS, JSON.stringify(updatedLinks));
 //   setTempUpdatedLinks(updatedLinks);
    setCustomizerOpen(false);
    
    setImageUploadOpen(false);

    
  };
  

  const handleIconSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
    selectedIcon = Number(e.target.value);
    (document.getElementById('url-update') as HTMLInputElement).disabled = false;
    console.log(selectedIcon);
  };

const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
  e.preventDefault();
  const files = (e.target as HTMLInputElement).files;

  if (files && files.length > 0) {
    const file = files[0];
    const reader = new FileReader();

    reader.onload = (readerEvent) => {
      const img = document.createElement('img');
      img.src = readerEvent.target?.result as string;
      img.onload = () => {
        const width = img.width;
        const height = img.height;
        const size = Math.min(width, height);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (ctx) {
          canvas.width = size;
          canvas.height = size;
          ctx.drawImage(
            img,
            (width - size) / 2, 
            (height - size) / 2, 
            size,                
            size,                
            0,                   
            0,                  
            size,               
            size               
          );

          // Get the base64 data from the canvas
          const base64Data = canvas.toDataURL('image/png');

          // Process the base64 data (for example, updating the icon)
          const updatedLinks = [...JSON.parse(sneakyLinks)];
          updatedLinks[selectedIcon].src = base64Data;
          setSneakyLinks(JSON.stringify(updatedLinks));
          setImageUploaded(true);
        }
      };

      // Handle error if the image fails to load
      img.onerror = () => {
        alert('There was an error loading the image.');
      };
    };

    reader.readAsDataURL(file);  // Read the file as a Data URL
  } else {
    alert('No file selected.');
  }
};

  const mixpanel = useMixpanel();
  const imageLabel = "Upload custom icon? (leave unchecked for image from web)"
  const [sneakyLinks, setSneakyLinks] = useState(
    storage.getLocalStorageDefault(StorageKeys.LINKS, JSON.stringify(initialSneakyLinks))
  );

  
  const [isCustomizerOpen, setCustomizerOpen] = useState(false);
  // const [tempUpdatedLinks, setTempUpdatedLinks] = useState<SneakyLink[]>(JSON.parse(JSON.stringify(sneakyLinks)));
  const [isImageUploadOpen, setImageUploadOpen] = useState(false);
  const [isImageUploaded, setImageUploaded] = useState(false);

  return (
    <div className="sneaky-links">
   
      <Modal keyboard={true} animation={true} show={isCustomizerOpen} onHide={() => setCustomizerOpen(false)}>
      <Modal.Header>
          <Modal.Title>Customize Quick Links</Modal.Title>

        </Modal.Header>
        
        <Form onSubmit={handleUpdate}>
          <Container>
        
        
            <Row><p> Select an icon to replace:</p></Row>
            <Row>
              {JSON.parse(sneakyLinks).map((link : SneakyLink) => (
                <Col className="d-flex justify-content-center"> 
                  <Image className='link-icon'id="slot1" src={link.src} width="400px" height="400px" thumbnail /> 
                </Col>
              ))}
            </Row>
           
            <Row>
              {JSON.parse(sneakyLinks).map((link : SneakyLink) => (
                  <Col className="d-flex justify-content-center">
                  <Form.Check name="group1" value={link.pos} type={'radio'} onChange={handleIconSelection} id={'option1'}/>
                </Col>
              ))}
            </Row>
         
          
    
          <Form.Label>Enter new url to replace selected icon:</Form.Label>
          <Form.Control id="url-update" disabled={true} type="text" placeholder="www.princeton.edu"/>

                
          <Form.Check name="group2" type="checkbox" label={imageLabel} onChange={(e) => {{setImageUploadOpen(!isImageUploadOpen)} {setImageUploaded(false)}}} />
          {isImageUploadOpen && <Form.Control  type="file" accept=".jpg, .jpeg, .png, .gif" onChange={handleImageUpload} />}
          </Container>
        
        
        <Button 
              variant="primary"
              type="submit"
              className="mt-3"        
            >
              Update!
            </Button>
        </Form>
      </Modal>
      <Container
    style={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-start',  // Align content to the top
      height: '15vh',  // Make sure the container fills the full height of the screen
    }}
  >
    {/* Header Section */}
    <Row
      style={{
        display: 'flex',
        justifyContent: 'space-between', // Space out the columns
        alignItems: 'center', // Align items vertically centered
        marginBottom: '20px',
      }}
    >
      <Col>
        <h3 style={{ color: 'white' }} className="bold">Sneaky Links</h3>
      </Col>
      <Col
        style={{
          display: 'flex',
          justifyContent: 'flex-end', // Align the button to the right
        }}
      >
        <Button
          variant="primary"
          id="customizer-button"
          className="customizer-button ml-auto"
          type="submit"
          onClick={() => setCustomizerOpen(true)}
        >
          <FiEdit2 />
        </Button>
      </Col>
    </Row>

    {/* Link Icons Section */}
    <Row
      style={{
        display: 'flex',
        flexWrap: 'wrap', // Ensure icons wrap in smaller screens
        justifyContent: 'center', // Center items horizontally
        gap: '20px', // Add some space between the icons
      }}
    >
      {JSON.parse(sneakyLinks).map((link: SneakyLink) => (
        <Col
         
          className="d-flex justify-content-center"
          key={link.id}
        >
          <a
            href={link.href}
            onClick={() => mixpanel.trackEvent(EventTypes.LINKS_CLICK, link.id)}
          >
            <img
              alt={link.alt}
              className="link-icon"
              src={link.src}
              style={link.style}
            />
          </a>
        </Col>
      ))}
    </Row>
  </Container>

      
    </div>
  );
}

export default SneakyLinksTable;

