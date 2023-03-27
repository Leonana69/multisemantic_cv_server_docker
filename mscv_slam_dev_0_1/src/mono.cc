#include <iostream>
#include <algorithm>
#include <fstream>
#include <chrono>
#include <vector>
#include <stdio.h>

#include "crow.h"

#include <opencv2/core/core.hpp>
#include "System.h"

using namespace std;
using namespace cv;

ORB_SLAM3::System* ptr_slam;

int main(int argc, char **argv) {
    if (argc != 4) {
        cerr << endl << "Usage: ./mscv_slam_dev_service path_to_vocabulary path_to_settings PORT" << endl;        
        return 1;
    }

    // Create SLAM system. It initializes all system threads and gets ready to process frames.
    ORB_SLAM3::System SLAM(argv[1], argv[2], ORB_SLAM3::System::MONOCULAR, true);
    ptr_slam = &SLAM;

    crow::SimpleApp app;

    CROW_ROUTE(app, "/slam").methods("POST"_method)
    ([](const crow::request& req) {
        char buffer[100];
        auto data = crow::json::load(req.body);
        crow::json::wvalue x({{}});
        if (!data) {
            return crow::response(crow::status::BAD_REQUEST); // same as crow::response(400)
        } else if (data["reset"].i() == 1) {
            ptr_slam->Reset();
            x["output"] = "reset";
        } else {
            auto w = data["width"].i();
            auto h = data["height"].i();
            auto t = data["timestamp"].d();
            cout << "Width: " << w << ", height: " << h << ", t: ";
            cout << std::setprecision(20) << (double)t << endl;

            Mat mat_img(h, w, CV_8UC3);
            crow::json::rvalue* rv_img = data["img"].begin();
            unsigned char *ptr = mat_img.data;
            for (auto& x : *rv_img) {
                *ptr = (unsigned char)x.i();
                ++ptr;
            }

            float* s = ptr_slam->TrackMonocular(mat_img, t).data();
            for (int i = 0; i < 4; i++) {
                cout << s[i] << ", ";
            }
            cout << endl;
            
            sprintf(buffer, "{ \'x\': %f, \'y\': %f, \'z\': %f, \'w\': %f }", s[0], s[1], s[2], s[3]);
            x["output"] = buffer;
        }
        
        return crow::response(x);
    });

    int PORT = atoi(argv[3]);
    app.port(PORT).run();
    
    // Stop all threads
    ptr_slam->Shutdown();
    return 0;
}