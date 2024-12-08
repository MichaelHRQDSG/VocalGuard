
// import React, { useState, useEffect } from 'react';
// import './ImageSlider.css'; // 导入样式

// const images = [
//   {
//     src: '/imgs/cyber-threats.jpg',
//     title: 'Cyber Threats',
//     description: 'Stay ahead of the latest cyber threats and protect your assets.',
//     buttonText: 'Learn More'
//   },
//   {
//     src: '/imgs/voice3.jpg',
//     title: 'Voice Security',
//     description: 'Enhance security with voice recognition technology.',
//     buttonText: 'Discover'
//   },
//   {
//     src: '/imgs/art1.jpg',
//     title: 'Digital Art AI',
//     description: 'Explore the possibilities of AI in digital art.',
//     buttonText: 'Explore'
//   }
// ];

// const ImageSlider = () => {
//   const [currentIndex, setCurrentIndex] = useState(0);

//   // 自动播放
//   useEffect(() => {
//     const interval = setInterval(() => {
//       setCurrentIndex((prevIndex) =>
//         prevIndex === images.length - 1 ? 0 : prevIndex + 1
//       );
//     }, 5000); // 5秒切换一次
//     return () => clearInterval(interval); // 清除定时器
//   }, []);

//   // 手动切换
//   const goToSlide = (index: number) => {
//     setCurrentIndex(index);
//   };

//   return (
//     <div className="slider">
//       <div
//         className="slider-inner"
//         style={{ transform: `translateX(-${currentIndex * 100}%)` }}
//       >
//         {images.map((image, index) => (
//           <div className="slider-item" key={index}>
//             <img src={image.src} alt={`Slide ${index + 1}`} />
//             <div className="slider-text">
//               <h2>{image.title}</h2>
//               <p>{image.description}</p>
//               <button className="slider-button">{image.buttonText}</button>
//             </div>
//           </div>
//         ))}
//       </div>
//       <div className="slider-controls">
//         {images.map((_, index) => (
//           <button
//             key={index}
//             className={`slider-dot ${index === currentIndex ? 'active' : ''}`}
//             onClick={() => goToSlide(index)}
//           />
//         ))}
//       </div>
//     </div>
//   );
// };

// export default ImageSlider;
// import React, { useState, useEffect } from 'react';
// import { Box, Typography, Button, Container, IconButton } from '@mui/material';
// import CircleIcon from '@mui/icons-material/Circle';

// const images = [
//   {
//     src: '/imgs/cyber-threats.jpg',
//     title: 'Cyber Threats',
//     description: 'Stay ahead of the latest cyber threats and protect your assets.',
//     buttonText: 'Learn More'
//   },
//   {
//     src: '/imgs/voice3.jpg',
//     title: 'Voice Security',
//     description: 'Enhance security with voice recognition technology.',
//     buttonText: 'Discover'
//   },
//   {
//     src: '/imgs/art1.jpg',
//     title: 'Digital Art AI',
//     description: 'Explore the possibilities of AI in digital art.',
//     buttonText: 'Explore'
//   }
// ];

// const ImageSlider = () => {
//   const [currentIndex, setCurrentIndex] = useState(0);

//   // Auto-play functionality
//   useEffect(() => {
//     const interval = setInterval(() => {
//       setCurrentIndex((prevIndex) =>
//         prevIndex === images.length - 1 ? 0 : prevIndex + 1
//       );
//     }, 5000); // 5 seconds interval
//     return () => clearInterval(interval); // Clear interval on component unmount
//   }, []);

//   // Manual slide change
//   const goToSlide = (index: number) => {
//     setCurrentIndex(index);
//   };

//   return (
//     <Container sx={{ position: 'relative', overflow: 'hidden', width: '100%', py: 4 }}>
//       <Box
//         sx={{
//           display: 'flex',
//           transition: 'transform 1s cubic-bezier(0.25, 0.1, 0.25, 1)', // Smooth scrolling
//           transform: `translateX(-${currentIndex * 100}%)`,
//           whiteSpace: 'nowrap'
//         }}
//       >
//         {images.map((image, index) => (
//           <Box
//             key={index}
//             sx={{
//               flex: '0 0 100%',
//               position: 'relative',
//               textAlign: 'center',
//               overflow: 'hidden',
//               height: 600, // Increased height for larger images
//             }}
//           >
//             <Box
//               component="img"
//               src={image.src}
//               alt={`Slide ${index + 1}`}
//               sx={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 2 }}
//             />
//             <Box
//               sx={{
//                 position: 'absolute',
//                 top: '50%',
//                 left: '50%',
//                 transform: 'translate(-50%, -50%)',
//                 color: 'white',
//                 textShadow: '0px 0px 8px rgba(0, 0, 0, 0.7)',
//                 textAlign: 'center',
//               }}
//             >
//               <Typography variant="h4" sx={{ mb: 1 }}>{image.title}</Typography>
//               <Typography variant="body1" sx={{ mb: 2 }}>{image.description}</Typography>
//               <Button variant="contained" color="primary">{image.buttonText}</Button>
//             </Box>
//           </Box>
//         ))}
//       </Box>
//       <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
//         {images.map((_, index) => (
//           <IconButton
//             key={index}
//             color={index === currentIndex ? 'primary' : 'default'}
//             onClick={() => goToSlide(index)}
//             size="small" // Smaller button size for navigation dots
//             sx={{ mx: 0.5 }} // Adjust margin if needed
//           >
//             <CircleIcon fontSize="small" />
//           </IconButton>
//         ))}
//       </Box>
//     </Container>
//   );
// };

// export default ImageSlider;
import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Button, Container, IconButton } from '@mui/material';
import CircleIcon from '@mui/icons-material/Circle';

const images = [
  {
    src: '/imgs/art1.jpg',
    title: 'Learning Uploads',
    description: 'We support personal and company information uploads, Learning how to upload files to use our system!.',
    buttonText: 'Learn More',
    target: 'cyber-threats-section',
  },
  {
    src: '/imgs/voice3.jpg',
    title: 'Voice Security',
    description: 'We will detect your potential threat in multidimesions!',
    buttonText: 'Discover',
    target: 'detection-section',
  },
  {
    src: '/imgs/cyber-threats.jpg',
    title: 'Reverification and Plan',
    description: 'We will give you Digital Reverification and Make a plan for your threat!',
    buttonText: 'Explore',
    target: 'reverification-plan-section',
  },
];

const sections = [
  {
    id: 'uploads-section',
    title: 'Upload',
    images: ['/imgs/personal_file_upload.png', '/imgs/company_file.png'],
    description: 'Learn how to identify and mitigate cyber threats effectively.',
  },
  {
    id: 'detection-section',
    title: 'Detection Pipeline',
    images: ['/imgs/detection.png'],
    description: 'Discover the cutting-edge threat Detection technology in VocalGuard.',
  },
  {
    id: 'reverification-plan-section',
    title: 'Reverification and Plan',
    images: ['/imgs/verify_2.png'],
    description: 'Here are what VocalGuard did to protect your security a step more.',
  }
];

const ImageSlider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Refs for the sections
  const sectionRefs = useRef<React.RefObject<HTMLDivElement>[]>(
    sections.map(() => React.createRef<HTMLDivElement>())
  );

  // Auto-play functionality
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) =>
        prevIndex === images.length - 1 ? 0 : prevIndex + 1
      );
    }, 5000); // 5 seconds interval
    return () => clearInterval(interval); // Clear interval on component unmount
  }, []);

  // Function to handle smooth scroll
  const scrollToSection = (index: number) => {
    sectionRefs.current[index]?.current?.scrollIntoView({
      behavior: 'smooth', // Smooth scrolling
      block: 'start',
    });
  };

  return (
    <Box>
      {/* Image Slider Section */}
      <Container sx={{ position: 'relative', overflow: 'hidden', width: '100%', py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            transition: 'transform 1s cubic-bezier(0.25, 0.1, 0.25, 1)', // Smooth scrolling
            transform: `translateX(-${currentIndex * 100}%)`,
            whiteSpace: 'nowrap',
          }}
        >
          {images.map((image, index) => (
            <Box
              key={index}
              sx={{
                flex: '0 0 100%',
                position: 'relative',
                textAlign: 'center',
                overflow: 'hidden',
                height: 600, // Increased height for larger images
              }}
            >
              <Box
                component="img"
                src={image.src}
                alt={`Slide ${index + 1}`}
                sx={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 2 }}
              />
              <Box
                sx={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  color: 'white',
                  textShadow: '0px 0px 8px rgba(0, 0, 0, 0.7)',
                  textAlign: 'center',
                }}
              >
                <Typography variant="h4" sx={{ mb: 1 }}>{image.title}</Typography>
                <Typography variant="body1" sx={{ mb: 2 }}>{image.description}</Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => scrollToSection(index)}
                >
                  {image.buttonText}
                </Button>
              </Box>
            </Box>
          ))}
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
          {images.map((_, index) => (
            <IconButton
              key={index}
              color={index === currentIndex ? 'primary' : 'default'}
              onClick={() => setCurrentIndex(index)}
              size="small"
              sx={{ mx: 0.5 }}
            >
              <CircleIcon fontSize="small" />
            </IconButton>
          ))}
        </Box>
      </Container>

      {/* Section Details */}
      {sections.map((section, index) => (
  <Box
    ref={sectionRefs.current[index]}
    key={section.id}
    id={section.id}
    sx={{ py: 6, textAlign: 'center' }}
  >
    <Container>
      <Typography variant="h3" sx={{ mb: 4 }}>{section.title}</Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>{section.description}</Typography>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column', // 纵向排列
          alignItems: 'center', // 居中对齐
          gap: 4, // 间距
        }}
      >
        {section.images.map((src, imgIndex) => (
          <Box
            component="img"
            key={imgIndex}
            src={src}
            alt={`Image ${imgIndex + 1}`}
            sx={{
              width: { xs: '100%', md: '60%' }, // 保持比例，宽度限制
              height: 'auto', // 自动调整高度以保持比例
              borderRadius: 2, // 圆角
              boxShadow: 2, // 阴影
            }}
          />
        ))}
      </Box>
    </Container>
  </Box>
))}
<Box
    component="footer"
    sx={{
      py: 4,
      textAlign: 'center',
      backgroundColor: '#f5f5f5',
      mt: 4, // 添加与内容的间距
    }}
  >
    <Container>
      <Typography variant="body2" color="textSecondary">
        © 2024 by Wendy(Yuanyuan He) & Michael(Renqiang He). All rights reserved.
      </Typography>
    </Container>
  </Box>
    </Box>
  );
};

export default ImageSlider;
