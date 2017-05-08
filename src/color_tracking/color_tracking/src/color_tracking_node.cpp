/*
 *  To run off a webcam comment lines 9-11
 *  call image_source using 1
 *  to run using ROS uncomment lines 9-11
 *  call image_source using 0
 * */

// Uncomment this block to run on ROS these are catkin components
// that get linked using the CMakeRequiredments.txt
#include <ros/ros.h>
#include <cv_bridge/cv_bridge.h>
#include <image_transport/image_transport.h>
#include "std_msgs/String.h"
#include <sstream>

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <stdlib.h>
//
#include <ctime>
#include <iostream>


#ifdef MEASURE_TIME
t_begin = clock();
#endif


/*
 * optimizations:
 * minimize the number of new mats made. So far we could rewrite the ones we have
 * but I am not to allow more flexibility in the future
 *
 */

// ########## GLOBALS ########
using namespace std;
// low to filter out orange
int iLowH = 0;
int iHighH = 8;

int iLowH_2 = 162;
int iHighH_2 = 179;

int iLowS = 146;
int iHighS = 255;

int iLowS_2 = 146;
int iHighS_2 = 255;

int iLowV = 77;
int iHighV = 255;

int iLowV_2 = 77;
int iHighV_2 = 255;

int blur1 = 1;
int blur2 = 1;

int param1 = 1;
int param2 = 1;

cv::RNG rng(12345);
// ########  End Globals #######

int myMin(int a, int b){
    if (a < b){
        return a;
    }
    else{
        return b;
    }
}

int myMax(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

string rel_location (cv::Point center, cv::Size s){
    // if center of circle < 1/3 of screen left, if greater than 2/3 right, else center.
    return (center.x < s.width/3) ? "Left" : (center.x > s.width * 2/3) ? "Right" : "Center";
}

string report_status(cv::Mat & raw_img, bool circle_found, cv::Point center, float radius){
    // text with status
    string dir = "";
	string msg = "";
    if (circle_found){
		ostringstream ss;
		ss << radius;
		msg = "Detected "+ ss.str();
        dir = rel_location(center, raw_img.size());
    }
    else{
        dir = "Not Detected";
		msg = "Not Detected";
    }
    cv::putText(raw_img, dir, cv::Point(raw_img.size().width / 12, raw_img.size().height* 11/12), cv::FONT_HERSHEY_SIMPLEX, 2, cvScalar(0,255,2), 3, CV_AA);
	return msg;
}

void circle_data (cv::Mat img, cv::Point center, int radius){

    //make a circle
    cv::circle(img, center, radius, cv::Scalar(0, 255, 0), 3);

    //make a cross
    cv::line(img,cv::Point(center.x - radius, center.y - radius), cv::Point(center.x + radius, center.y + radius), cv::Scalar(0,255,0), 1);
    cv::line(img,cv::Point(center.x - radius, center.y + radius), cv::Point(center.x + radius, center.y - radius), cv::Scalar(0,255,0), 1);
	//cv::imshow ("detected", img);
	// publish circle radious
}

void detectCircles (const cv::Mat& input_img, cv::Mat& raw_img, cv::Point &center, bool &detected, float & rad){

    // vector of circle objects
    vector<cv::Vec3f> circles;
    //TODO this is crappy detection

    // populate our vector of circle objects with all the circles we can find, we only care for one.
    //TODO get the circle with the highest radius I suppose.
    cv::HoughCircles(input_img, circles, CV_HOUGH_GRADIENT, 1, input_img.rows/12, myMax(param1,1), myMax(param2,1), 0, 0);

    if (circles.size() > 0){
        detected = false;
        // hard coded to only render 1 circle  change 1 to  circles.size() or your favorite number of circles
         	for(size_t current_circle = 0; current_circle < 1; ++current_circle) {
					rad = circles[current_circle][2];
					if (rad > 5.0){
							detected = true;
							center = cv::Point(round(circles[current_circle][0]), round(circles[current_circle][1]));
							circle_data(raw_img, center, round(circles[current_circle][2]));
					}	
            }
    }
}

int check_webcam(const cv::VideoCapture & cap){

    // Break if webcam does not work

    if ( !cap.isOpened() )  // if device is not accessible
    {
        cout << "Cannot open webcam" << endl;
        return 0;
    }
    else{
        return 1;
    }
} 
//#define MEASURE_TIME 1
#define COLOR_TRACKING 1

#ifdef MEASURE_TIME
clock_t t_begin = 0;
#endif


void make_control(){

    cv::namedWindow("sliders", CV_WINDOW_AUTOSIZE); //create a sliders window
    // (tag, window, data field, start)
    cvCreateTrackbar("LowH", "sliders", &iLowH, 179); //Hue (0 - 179)
    cvCreateTrackbar("HighH", "sliders", &iHighH, 179);
    cvCreateTrackbar("LowH_2", "sliders", &iLowH_2, 179);
    cvCreateTrackbar("HighH_2", "sliders", &iHighH_2, 179);

    cvCreateTrackbar("LowS", "sliders", &iLowS, 255); //Saturation (0 - 255)
    cvCreateTrackbar("HighS", "sliders", &iHighS, 255);
    cvCreateTrackbar("LowS_2", "sliders", &iLowS_2, 255);
    cvCreateTrackbar("HighS_2", "sliders", &iHighS_2, 255);

    cvCreateTrackbar("LowV", "sliders", &iLowV_2, 255); //Value (0 - 255)
    cvCreateTrackbar("HighV", "sliders", &iHighV_2, 255);
    cvCreateTrackbar("LowV_2", "sliders", &iLowV_2, 255);
    cvCreateTrackbar("HighV_2", "sliders", &iHighV_2, 255);


    cvCreateTrackbar("blur_1", "sliders", &blur1, 100);
    cvCreateTrackbar("blur_2", "sliders", &blur2, 100);

    cvCreateTrackbar("param1", "sliders", &param1, 200);
    cvCreateTrackbar("param2", "sliders", &param2, 200); 

}

string cv_color_tracking(const cv::Mat &imgHSV, cv::Mat &imgThresholded_red_1, cv::Mat &imgThresholded_red_2, cv::Mat &Raw){
    // an HSV image, and two blank threshold Mats, result is saved in third parameter ( thresholded_red_2 )

    // filter all hsv values that are not defined by us (or our sliders)
    cv::inRange(imgHSV, cv::Scalar(iLowH, iLowS, iLowV), cv::Scalar(iHighH, iHighS, iHighV), imgThresholded_red_1); //Threshold the image
    cv::inRange(imgHSV, cv::Scalar(iLowH_2, iLowS_2, iLowV_2), cv::Scalar(iHighH_2, iHighS_2, iHighV_2), imgThresholded_red_2); //Threshold the image

    // superimpose both images to gather all red from both ranges of the HSV sprectrum
    imgThresholded_red_2 = imgThresholded_red_1 | imgThresholded_red_2;

    //morphological opening (remove small objects from the foreground)
    cv::erode(imgThresholded_red_2, imgThresholded_red_2, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(5, 5)) );
    cv::dilate( imgThresholded_red_2, imgThresholded_red_2, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(5, 5)) );

    // I am not sure if we really need to do this twice.
    //morphological closing (fill small holes in the foreground)
    cv::erode(imgThresholded_red_2, imgThresholded_red_2, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(5, 5)) );
    cv::dilate( imgThresholded_red_2, imgThresholded_red_2, cv::getStructuringElement(cv::MORPH_ELLIPSE, cv::Size(5, 5)) );

    //cv::imshow("Erode + Dilate", imgThresholded_red_2); //show the thresholded image

    cv::Point center;
    bool circle_detected = false;
	float rad = 0;
    detectCircles(imgThresholded_red_2, Raw, center, circle_detected, rad);
	
    return report_status(Raw, circle_detected, center, rad);

}

void cv_publish_img(image_transport::Publisher &pub, cv::Mat& pub_img)
{
	//sensor_msgs::ImagePtr pub_msg = cv_bridge::CvImage(std_msgs::Header(), "bgr8", pub_img).toImageMsg();
	sensor_msgs::ImagePtr pub_msg = cv_bridge::CvImage(std_msgs::Header(), "mono8", pub_img).toImageMsg();
	pub.publish(pub_msg);
}


void imageCallback(const sensor_msgs::ImageConstPtr& msg_frame, image_transport::Publisher &pub, ros::Publisher &circle_pub)
{
    cv_bridge::CvImageConstPtr cv_ori_img_ptr;
    // capture image
	cv::Mat cv_ori_img;
    try{
        cv_ori_img = cv_bridge::toCvShare(msg_frame, "bgr8")->image;
    }catch(cv_bridge::Exception& e){
        ROS_ERROR("Could not convert from '%s' to 'bgr8'.", msg_frame->encoding.c_str());
    }


	cv::Mat cv_blank_mat;
	cv::Mat cv_color_detect_output;
	cv::Mat img_HSV;
	cv::cvtColor(cv_ori_img, img_HSV, cv::COLOR_BGR2HSV); //Convert the captured frame from BGR to HSV	

    // if you want to publish the edges, run this line (we don't want to, so far)
    //cv_RGB2Grey(cv_ori_img, cv_edge_output_img);
    //cv_publish_img(pub, cv_color_edge_output);

    // color detection, no idea why we are using the ifdef (TA) did it.
    #ifdef COLOR_TRACKING

//	int key =cv:: waitKey();
//	cout << " you pressed the r key dawg " << key << endl;

    string msg = cv_color_tracking(img_HSV, cv_blank_mat, cv_color_detect_output, cv_ori_img);
	std::stringstream ss;
	ss << msg;
	std_msgs::String pub_msg;	
	pub_msg.data = ss.str();
	circle_pub.publish(pub_msg);
		
    #endif

	// cv::imshow("raw_input", cv_ori_img); 

    // if you want to publish the color detection (we don't want to, so far)
    //cv_publish_img(pub, cv_color_detect_output);

    #ifdef MEASURE_TIME
    clock_t t_end = clock();
    double delta_time= double(t_end - t_begin) / CLOCKS_PER_SEC;
    // cout << "Delta_t = " << 1/delta_time << "\n";
    //t_begin = t_end;
    #endif

    // wait for "shutter" to have time to take a picture
    int k = cv::waitKey(30);
    #ifdef MEASURE_TIME
    t_begin = clock();
    #endif

}


int main(int argc, char **argv)
{
    //make_control();

    ros::init(argc, argv, "image_listener");

    ros::NodeHandle nh;
    
    image_transport::ImageTransport it(nh);
	
    ros::NodeHandle nh_pub;
    image_transport::ImageTransport itpub(nh_pub);
    image_transport::Publisher pub = itpub.advertise("sample/cannyimg", 1);
	ros::Publisher circle_pub = nh.advertise<std_msgs::String> ("circle_chatter", 256);

    #ifdef MEASURE_TIME
    t_begin = clock();
    #endif

    image_transport::Subscriber sub = it.subscribe("rgb/image_rect", 1, boost::bind(imageCallback, _1, pub, circle_pub));
    ros::spin();
    
}
