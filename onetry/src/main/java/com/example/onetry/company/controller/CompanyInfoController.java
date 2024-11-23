package com.example.onetry.company.controller;

import com.example.onetry.company.entity.CompanyExtraInfo;
import com.example.onetry.company.entity.CompanyInfo;
import com.example.onetry.company.service.CompanyInfoService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Tag(name = "[Company] 회사 정보를 불러옵니다.")
@RestController
@RequestMapping("/api/company-info")
@RequiredArgsConstructor
public class CompanyInfoController {
    private final CompanyInfoService companyInfoService;

    // 전체 CompanyInfo 목록 조회
    @Operation(summary = "전체 기업의 정보를 가져옵니다.", description = "전체 기업의 정보를 가져옵니다.")
    @GetMapping("/all")
    public ResponseEntity<List<CompanyInfo>> getAllCompanyInfo() {
        List<CompanyInfo> companyInfos = companyInfoService.getAllCompanyInfo();
        return ResponseEntity.ok(companyInfos);
    }

    // 전체 CompanyExtraInfo 목록 조회
    @Operation(summary = "전체 기업의 추가 정보를 가져옵니다.", description = "전체 기업의 추가 정보를 가져옵니다.")
    @GetMapping("/extra/all")
    public ResponseEntity<List<CompanyExtraInfo>> getAllCompanyExtraInfo() {
        List<CompanyExtraInfo> companyExtraInfos = companyInfoService.getAllCompanyExtraInfo();
        return ResponseEntity.ok(companyExtraInfos);
    }

    // 전체 CompanyInfo 목록 조회
    @Operation(summary = "id 값에 해당하는 기업의 정보를 가져옵니다.", description = "id값에 해당하는 기업의 정보를 가져옵니다.")
    @GetMapping("/{id}")
    public ResponseEntity<CompanyInfo> getCompanyInfo(@PathVariable("id") Long id) {
        CompanyInfo companyInfo = companyInfoService.getCompanyInfoById(id);
        return ResponseEntity.ok(companyInfo);
    }

    // 전체 CompanyExtraInfo 목록 조회
    @Operation(summary = "id 값에 해당하는 기업의 추가 정보를 가져옵니다.", description = "id 값에 해당하는 기업의 추가 정보를 가져옵니다.")
    @GetMapping("/extra/{id}")
    public ResponseEntity<CompanyExtraInfo> getCompanyExtraInfo(@PathVariable("id") Long id) {
        CompanyExtraInfo companyExtraInfo = companyInfoService.getCompanyExtraInfoById(id);
        return ResponseEntity.ok(companyExtraInfo);
    }

    // Company 이름 전체 조회 api
    @Operation(summary = "기업의 이름을 전부 조회합니다.", description = "기업의 이름을 전부 조회합니다.")
    @GetMapping("/name")
    public ResponseEntity<List<String>> getCompanyName(){
        List<String> companyNames = companyInfoService.getCompanyNames();
        return ResponseEntity.ok(companyNames);
    }

}
